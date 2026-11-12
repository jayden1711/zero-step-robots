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

This first design is a two-oscillator antiphase walking gait. Each joint is held by a PD servo around a rhythmic target, and torso balance feedback is added to both hips.

**Oscillators**
- Two oscillators, R and L, run at 1.0 Hz.
- They are coupled both ways with weight 2.0 and a lag of π, so they settle half a cycle apart.

**Phase plan per leg**
- **Stance (φ from 0 to π):** the thigh swings back, and the knee straightens to about 0 at φ = π/2.
- **Swing (φ from π to 2π):** the knee flexes to about −0.7 to clear the ground, and the thigh swings forward.

**Thigh (a0, a3)**
- The thigh tracks a target of −0.25 + 0.3·cos φ relative to the torso, with gains Kp = 1.0 and Kd = 0.1.
- Balance feedback is added to both thighs: −0.8·(torso angle − 0.2) − 0.1·(torso angular velocity).
- This holds a forward lean of about 0.2 rad. With that lean, the stance leg sweeps from about +0.25 to −0.35 rad from vertical, even though the hip can only bend backward.

**Knee (a1, a4)**
- The knee tracks −0.3 + 0.4·sin φ, with Kp = 1.5 and Kd = 0.1.

**Foot (a2, a5)**
- The foot holds a target of 0, with Kp = 1.0 and Kd = 0.05.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.09, "a1": -0.45, "a2": 0.0, "a3": -0.09, "a4": -0.45, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.1, "cos(R)": 0.3, "obs[1]": -0.8, "obs[10]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.6},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.1, "cos(L)": 0.3, "obs[1]": -0.8, "obs[10]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.6},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.01 | 1.17 | height too low
1 | -1.01 | 1.15 | height too low
2 | -1.03 | 1.18 | height too low
3 | -1.03 | 1.18 | height too low
4 | -1.02 | 1.18 | height too low
5 | -1.04 | 1.18 | height too low
6 | -1.02 | 1.16 | height too low
7 | -1.03 | 1.18 | height too low
8 | -1.03 | 1.16 | height too low
9 | -1.01 | 1.17 | height too low

Over the 10 episodes: mean d -1.02 m, min -1.04, max -1.01; mean time survived 1.17 s; mean forward speed -0.87 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.193 | 0.027 | 0.44 | 0.01
right leg | -0.523 | 0.003 | 0.20 | 0.00
right foot | -0.083 | 0.115 | 0.04 | 0.00
left thigh | -0.099 | 0.025 | 0.36 | 0.00
left leg | -0.518 | 0.002 | 0.22 | 0.00
left foot | -0.086 | 0.160 | 0.06 | 0.00
torso angle min -0.961, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.82 of the steps, 3 touchdowns
left foot: on the ground 0.75 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.03 | 1.20 | -0.120 | yes | yes | 0.65, 3.80
0.20 | -0.07 | 1.20 | -0.200 | yes | yes | 1.26, 4.40
0.30 | -0.12 | 1.20 | -0.288 | yes | yes | 1.91, 5.05
0.40 | -0.16 | 1.19 | -0.333 | yes | yes | 2.51, 5.65
0.50 | -0.22 | 1.18 | -0.344 | yes | yes | 3.17, 0.03
0.60 | -0.29 | 1.16 | -0.370 | yes | yes | 3.77, 0.63
0.70 | -0.37 | 1.14 | -0.450 | no | yes | 4.42, 1.28
0.80 | -0.46 | 1.12 | -0.507 | yes | yes | 5.03, 1.88
0.90 | -0.59 | 1.07 | -0.633 | yes | yes | 5.68, 2.54
1.00 | -0.73 | 1.00 | -0.756 | yes | no | 0.00, 3.14
1.10 | -0.91 | 0.90 | -0.884 | yes | no | 0.65, 3.80

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh: 0.00
R_knee: 0.00
R_foot: 0.00
L_thigh: 0.00
L_knee: 0.00
L_foot: 0.00

## Round 1: your reply

The robot fell backward within 1.2 s. The likely cause is that the torso feedback had the wrong sign.

**Diagnosis**
- From the start, the thigh torques were mostly positive, from the positive balance term and the +0.3·cos target. The torso angle then fell steadily toward −0.96 while both thighs sat at their 0 limit.
- The hip torque acts between the torso and the thigh. With the feet planted, a torque that raises the thigh angle turns the torso the other way, so it lowers obs[1].
- So the term −0.8·obs[1] amplified the backward lean instead of correcting it. Once a thigh reached its limit at 0, the robot tipped over as one rigid body.
- This contradicts the stated hint that "feedback opposes the sign of obs[1]". The round-0 data matches the reaction-torque reading, so I'm following the data.

**Changes**
- **Torso feedback sign flipped.** The thigh torque now gets +1.5·(obs[1] − 0.35) + 0.2·obs[10]. A negative torque lets the thigh swing back, which pitches the torso up toward a lean of +0.35. The +0.2·obs[10] term damps torso rotation.
- **Thighs moved off the joint limit.** The thigh target is now −0.4 + 0.3·cos φ, so it ranges from −0.1 to −0.7. The thigh never hits the 0 stop, and the hip torque always reaches the torso.
- **Thigh bias.** The bias is −0.4 − 1.5·0.35 = −0.925. At t = 0 the thighs push back right away, so the torso starts tipping forward instead of backward.
- **Unchanged:** the knee timing (straight in stance, flexed to about −0.7 in swing), the foot PD, and the 1 Hz antiphase oscillators.
- **What to check next round:** if this design moves toward −x, the stance and swing direction is reversed, and I'll flip the cos sign on the thighs.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.925, "a1": -0.45, "a2": 0.0, "a3": -0.925, "a4": -0.45, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.1, "cos(R)": 0.3, "obs[1]": 1.5, "obs[10]": 0.2},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.6},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.1, "cos(L)": 0.3, "obs[1]": 1.5, "obs[10]": 0.2},
    "range": 3.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.6},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

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

Over the 10 episodes: mean d -0.07 m, min -0.07, max -0.07; mean time survived 0.05 s; mean forward speed -1.48 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.994 | -0.005 | 0.94 | 0.83
right leg | 0.003 | 0.004 | 0.37 | 0.00
right foot | -0.011 | 0.017 | 0.06 | 0.00
left thigh | -0.988 | 0.001 | 1.00 | 1.00
left leg | -0.003 | 0.004 | 0.49 | 0.00
left foot | -0.009 | 0.016 | 0.06 | 0.00
torso angle min -0.878, max -0.005 rad; torso height min 1.18, max 1.25 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.00 of the steps, 0 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh: 0.00
R_knee: 0.00
R_foot: 0.00
L_thigh: 0.00
L_knee: 0.00
L_foot: 0.00

## Round 2: your reply

Round 1 was a mistake. Flipping the torso-feedback sign made things much worse: the robot fell in 0.05 s instead of 1.2 s.

**What the data shows**
- **Round 1, while airborne:** strong negative thigh torque swung both thighs back to −0.99. The torso pitched back to −0.88 at the same time.
- So negative hip torque lowers obs[1], as the task hint says. To correct a torso tilt, the thigh torque must oppose obs[1] and obs[10]. That is the round-0 sign.
- **Why round 0 fell:** both thighs sat at their 0 stop, which absorbed the corrective positive torque. The knees were bent about −0.5 with the feet flat.
- Bending a knee tilts the thigh's lower end forward. With a straight hip, that tips the torso backward, which matches the slow backward fall in round 0.
- **Consequence for the posture:** the hip and knee can only bend backward. The torso therefore has to lean slightly back so the legs can reach in front of the hip during stance.

**Changes**
- **Torso feedback:** the round-0 sign is back, with stronger damping: −1.0·(obs[1] + 0.2) − 0.4·obs[10]. The target torso angle is −0.2.
- **Thigh:** the target is −0.25 + 0.25·cos φ, so it ranges from 0 to −0.5, with Kp = 1.5 and Kd = 0.1.
  - Relative to vertical, the stance leg sweeps from about 0.2 rad in front to 0.3 rad behind.
  - The thighs now spend most of the cycle away from the 0 stop, so the corrective torque reaches the torso.
- **Knee:** the target is −0.25 + 0.55·sin φ, with Kp = 1.5.
  - In stance it is clipped straight at the joint limit, so the bend no longer pushes the torso back.
  - In swing it flexes to −0.8.
- **Unchanged:** the feet, the oscillators and the coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.575, "a1": -0.375, "a2": 0.0, "a3": -0.575, "a4": -0.375, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.5, "obs[11]": -0.1, "cos(R)": 0.375, "obs[1]": -1.0, "obs[10]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.5, "obs[14]": -0.1, "cos(L)": 0.375, "obs[1]": -1.0, "obs[10]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.41 | 0.86 | torso angle out of range
1 | -0.40 | 0.87 | torso angle out of range
2 | -0.41 | 0.88 | torso angle out of range
3 | -0.42 | 0.86 | torso angle out of range
4 | -0.40 | 0.89 | torso angle out of range
5 | -0.42 | 0.86 | torso angle out of range
6 | -0.43 | 0.88 | torso angle out of range
7 | -0.44 | 0.90 | torso angle out of range
8 | -0.40 | 0.85 | torso angle out of range
9 | -0.43 | 0.89 | torso angle out of range

Over the 10 episodes: mean d -0.42 m, min -0.44, max -0.40; mean time survived 0.87 s; mean forward speed -0.48 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.843 | 0.013 | 0.97 | 0.91
right leg | -0.730 | 0.030 | 0.48 | 0.00
right foot | -0.027 | 0.074 | 0.11 | 0.00
left thigh | -0.862 | 0.018 | 0.97 | 0.83
left leg | -0.757 | 0.030 | 0.43 | 0.00
left foot | -0.055 | 0.176 | 0.11 | 0.00
torso angle min -1.000, max -0.005 rad; torso height min 1.10, max 1.25 m
right foot: on the ground 0.44 of the steps, 7 touchdowns
left foot: on the ground 0.81 of the steps, 8 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.05 | 1.19 | -0.312 | yes | yes | 0.65, 3.80
0.20 | -0.10 | 1.18 | -0.578 | no | yes | 1.26, 4.40
0.30 | -0.14 | 1.16 | -0.713 | no | no | 1.91, 5.05
0.40 | -0.17 | 1.14 | -0.830 | yes | yes | 2.51, 5.65
0.50 | -0.20 | 1.13 | -0.900 | yes | yes | 3.17, 0.03
0.60 | -0.25 | 1.12 | -0.928 | no | yes | 3.77, 0.63
0.70 | -0.31 | 1.12 | -0.936 | no | yes | 4.42, 1.28
0.80 | -0.38 | 1.11 | -0.962 | no | yes | 5.03, 1.88

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh: 0.46
R_knee: 0.00
R_foot: 0.00
L_thigh: 0.46
L_knee: 0.00
L_foot: 0.00

## Round 3: your reply

Round 2 fell backward again, and I think the main cause was not posture but a numerical instability in the damping.

**Diagnosis**
- **The damping is too strong for the time step.** Each hip received about 0.5 × 100 Nm per rad/s of damping on the torso: 0.4 from obs[10] plus 0.1 from the thigh velocity. That acts on a torso that weighs about 3.7 kg, with inertia about the hip of about 0.2 kg·m². With 8 ms steps this gives c·dt/I ≈ 3. The damping term overshoots every step and the hip torque flips between +1 and −1.
- **This matches the data.**
  - The thigh actions were saturated 91% of the time.
  - The thigh units were saturated 46% of the time.
  - The torso still tipped back slowly, over about 0.8 s. That is the speed of gravity acting with near-zero average hip torque. A steady ±100 Nm hip torque would have moved it within milliseconds.
- **The backward bias has a second cause: the heel.** Each foot extends forward from the ankle, so the heel is at the ankle. Leaning the torso back puts the centre of mass behind the heel. I'm moving the torso target back to upright (0). The gait will then fall forward over a stance leg that sweeps from under the hip to behind it, which also gives a positive d.

**Changes**
- **Damping lowered.** Thigh Kd is 0.05 and the obs[10] gain is 0.05, about 0.1 per hip in total. The two hips together give roughly critical damping and stay well inside the stable range for an 8 ms step. The knee and foot damping stay modest; the foot's goes down to 0.03.
- **Thigh.** The target is −0.2 + 0.25·cos φ with Kp = 1.0, plus −1.0·obs[1] (target lean 0). The stance leg sweeps from under the hip to about 0.45 rad behind it.
- **Knee.** The target is −0.15 + 0.55·sin φ with Kp = 1.5.
  - In stance it is clipped straight.
  - In swing it flexes to about −0.7.
- **Unchanged:** the oscillators and the coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.2, "a1": -0.225, "a2": 0.0, "a3": -0.2, "a4": -0.225, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.05, "cos(R)": 0.25, "obs[1]": -1.0, "obs[10]": -0.05},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.05, "cos(L)": 0.25, "obs[1]": -1.0, "obs[10]": -0.05},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.06 | 1.31 | height too low
1 | -1.07 | 1.28 | height too low
2 | -1.06 | 1.31 | height too low
3 | -1.06 | 1.30 | height too low
4 | -1.05 | 1.31 | height too low
5 | -1.06 | 1.30 | height too low
6 | -1.06 | 1.30 | height too low
7 | -1.07 | 1.30 | height too low
8 | -1.09 | 1.29 | height too low
9 | -1.06 | 1.30 | height too low

Over the 10 episodes: mean d -1.06 m, min -1.09, max -1.05; mean time survived 1.30 s; mean forward speed -0.82 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.244 | 0.018 | 0.36 | 0.00
right leg | -0.510 | 0.017 | 0.30 | 0.00
right foot | -0.092 | 0.084 | 0.04 | 0.00
left thigh | -0.164 | 0.040 | 0.29 | 0.00
left leg | -0.543 | 0.017 | 0.26 | 0.00
left foot | -0.079 | 0.145 | 0.06 | 0.00
torso angle min -0.996, max -0.005 rad; torso height min 0.80, max 1.25 m
right foot: on the ground 0.70 of the steps, 5 touchdowns
left foot: on the ground 0.79 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.20 | -0.122 | yes | yes | 0.65, 3.80
0.20 | -0.05 | 1.20 | -0.188 | yes | yes | 1.26, 4.40
0.30 | -0.09 | 1.20 | -0.288 | yes | yes | 1.91, 5.05
0.40 | -0.12 | 1.19 | -0.302 | yes | yes | 2.51, 5.65
0.50 | -0.15 | 1.19 | -0.251 | yes | yes | 3.17, 0.03
0.60 | -0.20 | 1.19 | -0.250 | no | yes | 3.77, 0.63
0.70 | -0.26 | 1.18 | -0.326 | no | yes | 4.42, 1.28
0.80 | -0.34 | 1.16 | -0.377 | yes | yes | 5.03, 1.88
0.90 | -0.45 | 1.13 | -0.474 | yes | yes | 5.68, 2.54
1.00 | -0.57 | 1.10 | -0.543 | yes | no | 0.00, 3.14
1.10 | -0.70 | 1.07 | -0.573 | yes | no | 0.65, 3.80
1.20 | -0.85 | 1.00 | -0.694 | no | yes | 1.26, 4.40
1.30 | -1.06 | 0.80 | -0.996 | no | yes | 1.91, 5.05

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh: 0.00
R_knee: 0.00
R_foot: 0.00
L_thigh: 0.00
L_knee: 0.00
L_foot: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
