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

This first design uses PD tracking of rhythmic joint targets driven by two antiphase oscillators, plus torso balance feedback on the hips.

**Oscillators.** There are two, R and L, at 1 Hz. They are coupled both ways with lag π, so they lock in antiphase. With phase φ, stance is φ ∈ (0, π), where the thigh sweeps backward. Swing is φ ∈ (π, 2π), where the thigh comes forward and the knee flexes.

**Joint targets, per leg.** Each joint is one linear unit computing Kp·(target − q) − Kd·q̇. The constant part of each target goes into the bias.
- **Thigh:** the target is −0.3 + 0.3·cos φ, which spans the hip's allowed range of [−0.6, 0]. Kp is 1.5 and Kd is 0.15. Torso feedback of −1.5·obs[1] − 0.2·obs[10] is added, so a forward lean produces negative hip torque, which pitches the torso back. The bias holds a slight backward torso lean of about −0.05 rad, so the swing foot can reach a little ahead of the hip.
- **Knee:** the target is −0.4 + 0.4·sin φ. That is 0 (straight, at the joint limit) at mid-stance and −0.8 at mid-swing, for ground clearance. Kp is 2 and Kd is 0.15.
- **Ankle:** a PD hold at 0, with Kp 1 and Kd 0.1.

**Start.** The right leg starts at mid-stance (φ = π/2) and the left at mid-swing (φ = 3π/2). At those phases both thigh targets are −0.3, which avoids a jolt at t = 0.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.525, "a1": -0.8, "a2": 0.0, "a3": -0.525, "a4": -0.8, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.8, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.8, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.68 | 0.85 | torso angle out of range
1 | -0.68 | 0.88 | torso angle out of range
2 | -0.69 | 0.82 | torso angle out of range
3 | -0.69 | 0.86 | torso angle out of range
4 | -0.69 | 0.84 | torso angle out of range
5 | -0.64 | 0.95 | torso angle out of range
6 | -0.68 | 0.83 | torso angle out of range
7 | -0.69 | 0.89 | torso angle out of range
8 | -0.65 | 0.95 | torso angle out of range
9 | -0.68 | 0.86 | torso angle out of range

Over the 10 episodes: mean d -0.68 m, min -0.69, max -0.64; mean time survived 0.87 s; mean forward speed -0.78 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.658 | -0.005 | 0.97 | 0.79
right leg | -0.740 | 0.006 | 0.88 | 0.41
right foot | -0.036 | 0.122 | 0.40 | 0.05
left thigh | -0.645 | 0.028 | 0.96 | 0.73
left leg | -0.670 | 0.002 | 0.86 | 0.43
left foot | -0.042 | 0.158 | 0.49 | 0.00
torso angle min -0.999, max -0.005 rad; torso height min 1.01, max 1.25 m
right foot: on the ground 0.48 of the steps, 6 touchdowns
left foot: on the ground 0.76 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.07 | 1.18 | -0.476 | yes | yes | 2.22, 5.37
0.20 | -0.11 | 1.17 | -0.664 | yes | yes | 2.83, 5.97
0.30 | -0.16 | 1.16 | -0.720 | yes | yes | 3.48, 0.34
0.40 | -0.23 | 1.14 | -0.763 | yes | yes | 4.08, 0.94
0.50 | -0.33 | 1.13 | -0.851 | no | yes | 4.74, 1.60
0.60 | -0.42 | 1.10 | -0.948 | no | yes | 5.34, 2.20
0.70 | -0.51 | 1.07 | -0.969 | yes | yes | 5.99, 2.85
0.80 | -0.63 | 1.03 | -0.980 | yes | no | 0.31, 3.46

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.49
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_pd_balance: 0.49
L_knee_pd: 0.00
L_foot_pd: 0.00

## Round 1: your reply

Round 0 failed for one reason. At t = 0 both hips received a constant torque of about −0.5: the thigh-target offset plus the lean offset in the bias. With both feet down, that pitched the torso backward at about 5 rad/s. The torso feedback gain of 1.5 was far too weak to stop it, and the thigh units saturated half the time.

Changes for round 1:

- **Separate balance unit.** Torso balance now has its own unit, driving both hips: −3·(obs[1] + 0.2·obs[10]). This makes balance clearly stronger than the thigh tracking.
- **Weaker thigh tracking, near-zero starting torque.** The thigh PD is softer (Kp 1), with target −0.25 + 0.4·cos φ. The hip bias is now ≈ +0.05: the thigh offset (−0.25) is roughly cancelled by a small forward-lean setpoint (+0.1 rad × 3). There is no longer a large torque at the start.
- **Smaller knee flex.** The knee now flexes to −0.5 instead of −0.8, which limits the height drop and jolt at the start.
- **Wider ranges.** I raised the declared ranges so the units stop saturating.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.05, "a1": -0.5, "a2": 0.0, "a3": 0.05, "a4": -0.5, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
    "range": 2.0, "tol": 0.02, "to": {"a0": -3.0, "a3": -3.0}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.4, "obs[2]": -1.0, "obs[11]": -0.1},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.5, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.4, "obs[5]": -1.0, "obs[14]": -0.1},
    "range": 3.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.5, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.94 | 1.10 | height too low
1 | -0.95 | 1.10 | height too low
2 | -0.96 | 1.10 | height too low
3 | -0.96 | 1.10 | height too low
4 | -0.96 | 1.10 | height too low
5 | -0.97 | 1.11 | height too low
6 | -0.96 | 1.10 | height too low
7 | -0.97 | 1.11 | height too low
8 | -0.96 | 1.10 | height too low
9 | -0.96 | 1.10 | height too low

Over the 10 episodes: mean d -0.96 m, min -0.97, max -0.94; mean time survived 1.10 s; mean forward speed -0.87 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.014 | 0.038 | 0.80 | 0.55
right leg | -0.302 | 0.003 | 0.25 | 0.00
right foot | -0.085 | 0.014 | 0.04 | 0.00
left thigh | 0.001 | 0.042 | 0.97 | 0.83
left leg | -0.348 | 0.002 | 0.28 | 0.01
left foot | -0.057 | 0.160 | 0.07 | 0.00
torso angle min -0.941, max -0.005 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.77 of the steps, 3 touchdowns
left foot: on the ground 0.94 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.03 | 1.20 | -0.089 | yes | yes | 2.22, 5.37
0.20 | -0.06 | 1.20 | -0.142 | yes | yes | 2.83, 5.97
0.30 | -0.11 | 1.19 | -0.191 | yes | yes | 3.48, 0.34
0.40 | -0.17 | 1.19 | -0.244 | no | yes | 4.08, 0.94
0.50 | -0.23 | 1.18 | -0.269 | no | yes | 4.74, 1.60
0.60 | -0.30 | 1.17 | -0.313 | yes | yes | 5.34, 2.20
0.70 | -0.39 | 1.15 | -0.394 | yes | yes | 5.99, 2.85
0.80 | -0.49 | 1.11 | -0.485 | yes | yes | 0.31, 3.46
0.90 | -0.63 | 1.05 | -0.607 | yes | yes | 0.97, 4.11
1.00 | -0.78 | 0.96 | -0.755 | yes | yes | 1.57, 4.71

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
R_thigh_pd: 0.00
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_pd: 0.00
L_knee_pd: 0.00
L_foot_pd: 0.00

## Now: round 2 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
