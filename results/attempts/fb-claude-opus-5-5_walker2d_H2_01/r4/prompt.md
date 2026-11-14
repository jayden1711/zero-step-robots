# Task: design the controller network of a simulated walking robot

You will design the controller of a simulated robot. You cannot run code yourself. After each design you write, we
test it on 10 practice episodes and send you a fixed summary of the results; you then revise it. There are 6 designs in
total: this first one (round 0) and 5 revisions (rounds 1 to 5). Your round-5 design is final and is scored exactly as
written, on different episodes from the practice ones. There is no training: the numbers you write become the final
weights of the controller network.

## The robot and environment

Environment: Gymnasium `Walker2d-v5` (MuJoCo), a planar two-legged robot (torso; right and left thigh, leg and
foot) that moves in the x-z plane. Forward is +x.

- Observation `obs` (17 numbers, raw, not normalised; indices from 0):
  - obs[0]: height (z) of the torso
  - obs[1]: torso angle (radians)
  - obs[2]: right thigh joint angle
  - obs[3]: right leg joint angle
  - obs[4]: right foot joint angle
  - obs[5]: left thigh joint angle
  - obs[6]: left leg joint angle
  - obs[7]: left foot joint angle
  - obs[8]: torso x-velocity
  - obs[9]: torso z-velocity
  - obs[10]: torso angular velocity
  - obs[11] to obs[16]: angular velocities of the six joints, in the same order as obs[2] to obs[7]

  Velocities (obs[8] to obs[16]) are clipped to [-10, 10].
- Action (6 numbers): the torques at the right thigh, right leg, right foot, left thigh, left leg and left foot
  joints, in that order (a0 to a5). Values outside [-1, 1] are clipped to that range.
- One step is 0.008 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.005).

Episode rules:

- The walker is healthy while both hold: 0.8 < torso height z < 2.0, and -1 < torso angle < 1 (radians).
- The episode terminates as soon as the walker is not healthy. Otherwise it is cut off after 1000 steps.
- The environment's own reward per step is 1 (while healthy) + (torso x-velocity, measured over the step)
  - 0.001 * (sum of the squared action values, after clipping).

## Scoring

Your controller is run in 100 episodes of 1000 steps (8 seconds of simulated time) with fixed random seeds (the
seeds differ only in the tiny random perturbation of the initial state). For each episode we measure d, the forward
displacement of the torso along +x from the start to the last step at which the robot was still healthy (so the
fall that ends an episode earns nothing).

- Your score is the mean of d over the 100 episodes, in metres. Higher is better.
- The controller passes if the mean of d is at least 3 m and at least 50 of the 100 episodes reach d >= 3 m.

The environment's own reward is given above for completeness; it is not the score.
The controller is deterministic: it has no randomness.

## Design hint

A workable structure for this robot is a walking gait with the two legs in antiphase:

- Two oscillators, one per leg, coupled so that they settle half a cycle (pi radians) apart. Each leg alternates
  stance (on the ground, pushing the body forward, thigh swinging back) and swing (knee flexed to clear the ground,
  thigh swinging forward). The phase relationship between a leg's joints is fixed by how each joint's command is
  taken from that leg's oscillator's cos and sin outputs.
- Balance feedback is added on top of the rhythm: the torso angle (obs[1]) and the torso angular velocity
  (obs[10]) feed back to the thigh joints so the torso stays upright, and forward speed is regulated through how far
  the torso leans.

Facts and ranges (from the model files and the documentation, not tuned for you):

- Sign conventions. A positive torso angle (obs[1]) means the torso leans forward (towards +x). For every thigh,
  leg and foot joint, a positive torque drives the joint angle up, and a negative joint angle swings the part below
  the joint backwards (towards -x). Thigh and leg joint angles are limited to [-2.62, 0] radians (0 = straight in
  line with the part above), the feet to [-0.79, 0.79].
- With a foot on the ground, a negative torque at that leg's thigh pitches the torso backward (the reaction at
  the hip).
- Admissible ranges: oscillator frequency 0.5 to 2 Hz for the stride of a robot this size; rhythmic torque
  amplitude up to 1 (the action limit) per joint; feedback that holds the torso upright opposes the sign of
  obs[1] and of obs[10] at the stance-leg thigh.

## What you write: a circuit spec, compiled exactly into the controller network

The controller is a fixed network with up to 4 phase oscillators and one hidden layer of 16 tanh units. At every
step, with the current observation `obs`:

    y      = [cos(phase_1), sin(phase_1), ..., cos(phase_M), sin(phase_M)]     (oscillator outputs)
    h      = tanh(W1 @ [obs; y] + b1)                                          (16 hidden units)
    action = clip(W2 @ h + b2, -1, 1)
    then each phase advances by 0.008 s times its rate:
    d(phase_i)/dt = 2*pi*freq_i + sum_j weight_ji * sin(phase_j - phase_i - lag_ji) + sum_k feedback_ik * obs[k]

The phases start at their initial values at the beginning of every episode. There is no other memory.

You do not write W1, b1, W2, b2 directly. You write a spec; a deterministic compiler turns it into the exact
weights. Each unit of the spec uses one hidden unit (at most 16 units). Unit inputs are named `obs[k]` (k from 0 to
16), `cos(NAME)` or `sin(NAME)` for an oscillator called NAME. Actions are named `a0` to a5.

- `oscillators` (0 to 4): each has a `name` (letters, digits, underscore), `freq_hz` (its natural frequency),
  `phase0` (initial phase, radians) and optionally `feedback`, an object mapping `obs[k]` to a gain (radians per
  second per unit of obs[k]) that speeds the phase up or slows it down.
- `couplings` (optional): each `{"from": A, "to": B, "weight": w, "phase_lag": L}` adds
  `w * sin(phase_A - phase_B - L)` to the rate of B, pulling B towards lagging A by L radians (for w > 0).
- `bias` (optional): constant offsets added to actions, e.g. `{"a0": <number>}`.
- `units`, each one of:
  - `linear`: adds `to[a] * z` to each action a in `to`, where `z = sum of inputs[name] * value(name)`. It is
    realised by one tanh unit, so you must declare `range`, the largest |z| you need it to be linear for, and `tol`,
    the relative error you accept inside that range (0 < tol < 1, e.g. 0.01). Outside the range the unit saturates.
  - `reflex`: adds `to[a] * tanh(sharpness * (z - threshold))` to each action a in `to` (exact; sharpness > 0).

Output format: reply with one JSON object in a single ```json code block, nothing else in the block:

    {"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
     "oscillators": [{"name": "<name>", "freq_hz": <number>, "phase0": <number>, "feedback": {"obs[k]": <number>}}],
     "couplings": [{"from": "<name>", "to": "<name>", "weight": <number>, "phase_lag": <number>}],
     "bias": {"a<i>": <number>},
     "units": [
       {"type": "linear", "name": "<text>", "inputs": {"obs[k]": <number>, "sin(<name>)": <number>},
        "range": <number>, "tol": <number>, "to": {"a<i>": <number>}},
       {"type": "reflex", "name": "<text>", "inputs": {"cos(<name>)": <number>}, "threshold": <number>,
        "sharpness": <number>, "to": {"a<i>": <number>}}
     ]}

The `<...>` parts are placeholders for you to fill in; lists may have any length within the limits. Numbers must be
plain decimals (no expressions, no NaN or Infinity). You may write any explanation outside the code block. If the
reply has no valid block, or the spec does not compile, the controller scores as a failure (d = 0).

## Round 0: your reply

This is a first design. The task statement leaves one sign uncertain, so this round also tests it.

**A sign check that goes against the hint.** In the Walker2d model, the torso pitch and the thigh joint share the same hinge axis, so the thigh's angle in the world is the torso angle plus the thigh joint angle. With the stance foot planted, a positive thigh torque raises the thigh joint angle, which lowers the torso angle. That agrees with the given fact that a negative thigh torque pitches the torso backward. But it means the feedback that keeps the torso near zero should have the same sign as obs[1] and obs[10], not the opposite sign the hint says. I've used the same sign. If the robot falls within the first few hundred steps, this is the first thing to flip.

**Structure:**
- **Two oscillators (R and L).** Each runs at 0.9 Hz, starting π apart, with two-way coupling of weight 2 that holds them in antiphase.
- **Thigh unit (one per leg).** It drives the thigh joint towards a target that swings between −0.6 and 0 rad (−0.3 + 0.3·sin φ), with gain 2 and damping 0.2.
  - The same unit also adds torso balance: +2·obs[1] + 0.3·obs[10].
  - Stance is the part of the cycle where the thigh target is decreasing (cos φ < 0), so the leg moves backward and pushes the body forward.
- **Knee units.** A position-and-damping controller targets +0.1 rad (pressing slightly into the straight limit) during stance. A reflex unit switches the target to about −0.6 rad (knee flexed) when cos φ > 0.3, which covers the swing phase.
- **Foot unit.** It holds the foot near 0 rad with light damping.
- **Units used:** 8 of 16, leaving room for revisions.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.6, "a1": -0.5, "a3": -0.6, "a4": -0.5},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.6, "obs[2]": -2.0, "obs[11]": -0.2, "obs[1]": 2.0, "obs[10]": 0.3},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.3, "sharpness": 4.0,
    "to": {"a1": -0.7}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.6, "obs[5]": -2.0, "obs[14]": -0.2, "obs[1]": 2.0, "obs[10]": 0.3},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.3, "sharpness": 4.0,
    "to": {"a4": -0.7}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

**How I'll read the results:**
- **Very early falls (within about 100 steps):** the balance sign is wrong, so I'll flip it.
- **Negative d:** the gait is running in reverse, so I'll swap the sin sign or the swing condition.
- **Survives but barely moves:** I'll add a forward torso lean and larger stride or push-off.

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.07 | 0.05 | torso angle out of range
1 | -0.07 | 0.05 | torso angle out of range
2 | -0.07 | 0.05 | torso angle out of range
3 | -0.07 | 0.05 | torso angle out of range
4 | -0.07 | 0.05 | torso angle out of range
5 | -0.07 | 0.05 | torso angle out of range
6 | -0.07 | 0.05 | torso angle out of range
7 | -0.07 | 0.05 | torso angle out of range
8 | -0.07 | 0.05 | torso angle out of range
9 | -0.07 | 0.05 | torso angle out of range

Over the 10 episodes: mean d -0.07 m, min -0.07, max -0.07; mean time survived 0.05 s; mean forward speed -1.44 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.875 | -0.005 | 0.93 | 0.83
right leg | -0.073 | 0.003 | 0.68 | 0.33
right foot | -0.001 | 0.015 | 0.12 | 0.00
left thigh | -0.907 | 0.001 | 0.94 | 0.83
left leg | 0.002 | 0.010 | 0.15 | 0.00
left foot | -0.009 | 0.009 | 0.08 | 0.00
torso angle min -0.804, max -0.005 rad; torso height min 1.19, max 1.25 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.00 of the steps, 0 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.00
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_pd_balance: 0.00
L_knee_pd: 0.00
L_foot_pd: 0.00

## Round 1: your reply

# Round 1: flip the balance sign and fix the bias offsets

## What went wrong in round 0

The robot fell backward within 6 steps. The cause was a positive-feedback loop:

1. Both thighs started with large negative torque. That came from the -0.6 biases, and since sin φ = 0 at the start, nothing offset them.
2. That negative torque pitched the torso backward, to obs[1] < 0.
3. My balance term (+2·obs[1]) then made the thigh torque more negative still.
4. Both thighs saturated at -1, and the torso passed -1 rad almost immediately.

The data confirms what the task statement says: negative thigh torque pitches the torso backward. So my round-0 sign argument was wrong. The balance feedback must **oppose** the signs of obs[1] and obs[10], as the hint said.

The knee biases were also inconsistent. A -0.5 bias contradicted the "straight in stance" target.

## Changes for round 1

- **Balance feedback flipped**, and the gains lowered:
  - -1.5·obs[1] - 0.2·obs[10] per thigh.
  - Both thighs carry it, so the total is about 3 and 0.4.
  - A small positive bias (0.075) adds a slight forward lean, a torso target of about +0.05 rad.
- **Thigh target is now 0.3·sin φ**, centred on zero, with no large offset bias. Swing is when cos φ > 0.
- **Knees:**
  - Proportional-derivative control towards 0 rad, with gain 1.5 and damping 0.15, and no bias.
  - A reflex adds -0.8 during swing (cos φ > 0.3) and about +0.8 during stance, which locks the knee straight.
- **Feet:** hold at 0 rad, unchanged.
- **Oscillators:** unchanged, 0.9 Hz in antiphase.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.075, "a3": 0.075},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.6, "obs[2]": -2.0, "obs[11]": -0.2, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.3, "sharpness": 4.0,
    "to": {"a1": -0.8}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.6, "obs[5]": -2.0, "obs[14]": -0.2, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.3, "sharpness": 4.0,
    "to": {"a4": -0.8}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.08 | 1.62 | height too low
1 | -0.93 | 1.34 | height too low
2 | -1.10 | 1.58 | height too low
3 | -1.14 | 1.66 | height too low
4 | -1.07 | 1.73 | torso angle out of range
5 | -1.07 | 1.74 | height too low
6 | -1.11 | 1.60 | height too low
7 | -1.01 | 1.63 | height too low
8 | -0.93 | 1.35 | height too low
9 | -0.94 | 1.42 | height too low

Over the 10 episodes: mean d -1.04 m, min -1.14, max -0.93; mean time survived 1.57 s; mean forward speed -0.66 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.464 | 0.022 | 0.91 | 0.74
right leg | -0.533 | 0.043 | 0.67 | 0.33
right foot | -0.099 | 0.150 | 0.27 | 0.00
left thigh | -0.366 | 0.041 | 0.85 | 0.75
left leg | -0.489 | 0.030 | 0.75 | 0.29
left foot | -0.078 | 0.000 | 0.24 | 0.00
torso angle min -0.911, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.67 of the steps, 14 touchdowns
left foot: on the ground 0.43 of the steps, 15 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.20 | -0.084 | yes | yes | 0.59, 3.73
0.20 | -0.05 | 1.20 | -0.139 | yes | yes | 1.13, 4.27
0.30 | -0.06 | 1.20 | -0.072 | yes | yes | 1.72, 4.86
0.40 | -0.10 | 1.20 | -0.200 | yes | no | 2.26, 5.40
0.50 | -0.16 | 1.19 | -0.373 | yes | no | 2.85, 5.99
0.60 | -0.19 | 1.18 | -0.499 | yes | no | 3.39, 0.25
0.70 | -0.21 | 1.18 | -0.495 | yes | no | 3.98, 0.84
0.80 | -0.23 | 1.18 | -0.483 | yes | no | 4.52, 1.38
0.90 | -0.24 | 1.19 | -0.332 | no | yes | 5.11, 1.97
1.00 | -0.28 | 1.18 | -0.277 | no | yes | 5.65, 2.51
1.10 | -0.37 | 1.16 | -0.514 | yes | yes | 6.24, 3.10
1.20 | -0.46 | 1.12 | -0.661 | yes | yes | 0.50, 3.64
1.30 | -0.58 | 1.07 | -0.739 | yes | no | 1.09, 4.23
1.40 | -0.70 | 1.05 | -0.729 | yes | no | 1.63, 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.24
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_pd_balance: 0.20
L_knee_pd: 0.00
L_foot_pd: 0.00

## Round 2: your reply

# Round 2: stronger torso control, a speed term, and less thigh saturation

## Reading the round-1 results

- **The balance sign is now right.** Round 0 settled it: negative thigh torque pitched the torso backward almost at once, so the feedback must oppose obs[1] and obs[10], as in round 1.
- **The torso still drifted backward**, to between -0.5 and -0.74 rad, and the robot moved backward at about -0.66 m/s. It then "sat down" (height too low, knees near -0.5).
- **The balance terms lost out.** The thigh actions were saturated about 75% of the time, and the units were past their declared range 20 to 24% of the time. So the rhythm and the joint-angle terms were swamping the balance terms.
- **Why the torso drifts back:**
  - Each stance stroke (thigh moving backward) and each swing stroke (swing-leg reaction) pushes the torso backward.
  - My balance gain was too weak to undo that.
  - Nothing reacted to the robot moving backward.

## Changes for round 2

- **Balance is the priority.** The torso gains rise to -3.0·obs[1] - 0.4·obs[10] per thigh, about 6 and 0.8 in total.
- **Smaller thigh rhythm and joint gains.** The thigh target is now -0.2 + 0.2·sin φ, with gain 1.5 and damping 0.15. The range rises to 5 so the unit stays linear.
- **Speed feedback on both thighs: -0.3·obs[8].** When the robot slides backward (v < 0), this adds positive thigh torque, which pitches the torso forward and stops the backward run. When the robot goes fast, it leans the torso back. Together with the -0.2 joint offset, this gives a net thigh bias of about 0.
- **Firmer knees:**
  - The stance lock is stronger: gain 2, plus about +0.8 from the reflex.
  - The swing flexion starts a little earlier (cos φ > 0.2) and is a little stronger.
- **Feet:** stiffer hold at 0 rad.
- **Units used:** still 8 of 16.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.0, "a3": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.3, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -3.0, "obs[10]": -0.4, "obs[8]": -0.3},
    "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.2, "sharpness": 5.0,
    "to": {"a1": -0.9}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.5, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.3, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -3.0, "obs[10]": -0.4, "obs[8]": -0.3},
    "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.2, "sharpness": 5.0,
    "to": {"a4": -0.9}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.5, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## How I'll read the results

- **The torso still drifts back steadily:** I'll add a positive thigh bias (a forward-lean target) or raise the balance gain.
- **The torso oscillates or falls forward:** I'll lower the balance gain or the speed gain.
- **It is stable but d ≈ 0:** I'll raise the thigh amplitude and the speed set-point.

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.98 | 1.42 | height too low
1 | -0.99 | 1.41 | height too low
2 | -0.99 | 1.54 | height too low
3 | -0.98 | 1.41 | height too low
4 | -1.00 | 1.42 | height too low
5 | -1.00 | 1.42 | height too low
6 | -0.97 | 1.40 | height too low
7 | -1.00 | 1.42 | height too low
8 | -0.99 | 1.42 | height too low
9 | -0.98 | 1.42 | height too low

Over the 10 episodes: mean d -0.99 m, min -1.00, max -0.97; mean time survived 1.43 s; mean forward speed -0.69 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.074 | 0.049 | 0.76 | 0.36
right leg | -0.295 | 0.029 | 0.57 | 0.00
right foot | -0.077 | 0.151 | 0.08 | 0.00
left thigh | -0.036 | 0.042 | 0.70 | 0.44
left leg | -0.241 | 0.023 | 0.66 | 0.00
left foot | -0.069 | 0.026 | 0.05 | 0.00
torso angle min -0.937, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.91 of the steps, 2 touchdowns
left foot: on the ground 0.70 of the steps, 5 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.20 | -0.068 | yes | yes | 0.59, 3.73
0.20 | -0.05 | 1.20 | -0.107 | yes | yes | 1.13, 4.27
0.30 | -0.07 | 1.21 | -0.082 | yes | no | 1.72, 4.86
0.40 | -0.10 | 1.21 | -0.095 | yes | yes | 2.26, 5.40
0.50 | -0.13 | 1.20 | -0.135 | yes | yes | 2.85, 5.99
0.60 | -0.17 | 1.20 | -0.162 | yes | yes | 3.39, 0.25
0.70 | -0.21 | 1.19 | -0.196 | yes | yes | 3.98, 0.84
0.80 | -0.26 | 1.19 | -0.212 | yes | yes | 4.52, 1.38
0.90 | -0.30 | 1.19 | -0.174 | yes | yes | 5.11, 1.97
1.00 | -0.38 | 1.17 | -0.274 | yes | yes | 5.65, 2.51
1.10 | -0.48 | 1.14 | -0.381 | yes | yes | 6.24, 3.10
1.20 | -0.60 | 1.09 | -0.491 | yes | yes | 0.50, 3.64
1.30 | -0.77 | 0.98 | -0.687 | yes | no | 1.09, 4.23
1.40 | -0.95 | 0.84 | -0.917 | no | no | 1.63, 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.00
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_pd_balance: 0.00
L_knee_pd: 0.00
L_foot_pd: 0.00

## Round 3: your reply

# Round 3: lean the legs forward from the ankles, keep the hips off their limit, keep stance knees straight

## What round 2 shows

- **The balance sign is settled.** Every run is consistent with this: with a foot planted, the torso angle moves together with the thigh joint angle (obs[1] − thigh angle stays roughly constant), and positive thigh torque pitches the torso forward.
- **The hips could not act in the direction balance needed.** In round 2 the thighs stayed between −0.07 and +0.05 rad, which is the 0 limit. The torso tilted back, so the balance term asked for positive thigh torque. That only pushed the hips against their stop and did nothing.
  - The robot then tipped backward as one rigid inverted pendulum, legs in line with the torso and feet ahead of the hip.
  - Because the hips only extend (range ≤ 0), a backward tilt like this cannot be corrected at the hip.
- **The thighs never stepped.** The balance term kept them at the limit, so there were only 2 to 5 touchdowns.
- **Stance knee flexion makes it worse.** With hips that cannot flex, a bent stance knee (−0.3 to −0.5) forces the torso backward, which is the "sitting down" failure.
- **The ankles can only catch a forward fall.** The foot extends forward from the ankle (toe lever about 0.26 m, heel about 0.06 m). So the robot should be kept leaning slightly forward over its feet.

## Changes

- **Foot PD target is now +0.1 rad (toe-up), with gain 2.** With the foot flat, this holds the shanks tilted about 0.1 rad forward. The centre of mass then sits over the toe lever, which the ankle can hold. Because the legs are behind the body, the hips sit near −0.1 rad, away from the limit, so the balance torque has room to act in both directions.
- **Thigh target is −0.2 + 0.2·sin φ.** It moves between −0.4 and 0, with gain 0.8, so stance sweeps the leg backward. Torso balance is −2.5·obs[1] − 0.3·obs[10] per hip. Speed feedback is −0.15·obs[8]: at higher speed the torso leans back, so feet can land further forward and slow the robot.
- **Knees are straight in stance and flex more in swing.** The reflex now adds +1.2 in stance (locked at 0) and −1.2 when cos φ > 0.3, giving about −0.6 rad of flexion for clearance.
- **Start phases are now 1.87 and −1.27.** The right leg starts early in stance and the left starts early in swing. This avoids flexing a knee at t = 0 while both legs carry the weight.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.87},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.27}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.0, "a3": 0.0, "a2": 0.2, "a5": 0.2},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.16, "obs[2]": -0.8, "obs[11]": -0.08, "obs[1]": -2.5, "obs[10]": -0.3, "obs[8]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a1": -1.2}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -2.0, "obs[13]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.16, "obs[5]": -0.8, "obs[14]": -0.08, "obs[1]": -2.5, "obs[10]": -0.3, "obs[8]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a4": -1.2}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -2.0, "obs[16]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## How I'll read the results

- **It still tips backward with the thighs near 0:** I'll raise the foot toe-up target or add a negative thigh bias.
- **It falls forward quickly:** I'll lower the foot target, strengthen the speed feedback, or raise the frequency.
- **It stands but makes little progress:** I'll raise the thigh amplitude and add a toe-down push-off late in stance.

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.15 | 1.81 | height too low
1 | -1.18 | 1.72 | height too low
2 | -0.48 | 8.00 | cut off at 1000 steps
3 | -0.37 | 8.00 | cut off at 1000 steps
4 | -1.15 | 1.85 | height too low
5 | -1.27 | 5.74 | height too low
6 | -1.17 | 1.80 | height too low
7 | -1.24 | 2.36 | height too low
8 | -1.17 | 1.70 | height too low
9 | -1.15 | 1.80 | height too low

Over the 10 episodes: mean d -1.03 m, min -1.27, max -0.37; mean time survived 3.48 s; mean forward speed -0.48 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.099 | 0.048 | 0.72 | 0.41
right leg | -0.409 | 0.046 | 0.76 | 0.58
right foot | 0.004 | 0.157 | 0.08 | 0.00
left thigh | -0.150 | 0.048 | 0.66 | 0.35
left leg | -0.420 | 0.065 | 0.64 | 0.38
left foot | 0.000 | 0.169 | 0.08 | 0.00
torso angle min -0.926, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.68 of the steps, 5 touchdowns
left foot: on the ground 0.76 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.87, 5.01
0.10 | -0.02 | 1.20 | -0.069 | yes | yes | 2.46, 5.60
0.20 | -0.04 | 1.20 | -0.130 | yes | yes | 3.00, 6.14
0.30 | -0.06 | 1.20 | -0.168 | yes | yes | 3.59, 0.45
0.40 | -0.09 | 1.20 | -0.190 | yes | yes | 4.13, 0.99
0.50 | -0.10 | 1.20 | -0.120 | no | yes | 4.72, 1.58
0.60 | -0.14 | 1.20 | -0.166 | no | yes | 5.26, 2.12
0.70 | -0.16 | 1.20 | -0.175 | yes | yes | 5.85, 2.71
0.80 | -0.19 | 1.20 | -0.166 | yes | yes | 0.11, 3.25
0.90 | -0.24 | 1.19 | -0.198 | yes | yes | 0.70, 3.84
1.00 | -0.29 | 1.19 | -0.216 | yes | yes | 1.24, 4.38
1.10 | -0.32 | 1.20 | -0.149 | yes | no | 1.83, 4.97
1.20 | -0.38 | 1.19 | -0.185 | yes | yes | 2.37, 5.52
1.30 | -0.47 | 1.17 | -0.288 | yes | yes | 2.96, 6.10
1.40 | -0.56 | 1.15 | -0.380 | yes | yes | 3.50, 0.36

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.00
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_pd_balance: 0.00
L_knee_pd: 0.00
L_foot_pd: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
