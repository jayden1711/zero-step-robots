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

This is my round-0 design: two antiphase oscillators drive the legs, with torso-angle feedback on both thighs. It is untested, since I can't run it.

- **Gait:** each leg's oscillator is coupled to the other with a half-cycle lag, and runs at 1 Hz.
- **Thigh:** driven by `sin(phase)`, so it swings forward when sin is positive and back when negative.
- **Knee:** flexes during swing and is extended during stance, with a small constant bias toward straight for support.
- **Foot:** gets a small ankle command in phase with the thigh.
- **Balance:** a shared linear unit feeds the torso angle and angular velocity to both thighs with negative gains.

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
 "bias": {"a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.5}, "range": 1.0, "tol": 0.01, "to": {"a0": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(R)": -0.5, "cos(R)": -0.2}, "range": 1.0, "tol": 0.01, "to": {"a1": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"sin(R)": 0.2}, "range": 1.0, "tol": 0.01, "to": {"a2": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.5}, "range": 1.0, "tol": 0.01, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(L)": -0.5, "cos(L)": -0.2}, "range": 1.0, "tol": 0.01, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"sin(L)": 0.2}, "range": 1.0, "tol": 0.01, "to": {"a5": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -1.0, "obs[10]": -0.15}, "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.09 | 0.80 | height too low
1 | -0.10 | 0.80 | height too low
2 | -0.04 | 0.78 | height too low
3 | -0.05 | 0.79 | height too low
4 | -0.06 | 0.79 | height too low
5 | -0.05 | 0.78 | height too low
6 | -0.08 | 0.80 | height too low
7 | -0.05 | 0.78 | height too low
8 | -0.07 | 0.79 | height too low
9 | -0.09 | 0.80 | height too low

Over the 10 episodes: mean d -0.07 m, min -0.10, max -0.04; mean time survived 0.79 s; mean forward speed -0.09 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.769 | 0.030 | 0.51 | 0.23
right leg | -2.667 | 0.362 | 0.37 | 0.00
right foot | -1.031 | 0.852 | 0.13 | 0.00
left thigh | -0.525 | 0.041 | 0.36 | 0.20
left leg | -2.122 | 0.013 | 0.42 | 0.00
left foot | -0.197 | 0.919 | 0.13 | 0.00
torso angle min -0.640, max -0.004 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.13 of the steps, 1 touchdowns
left foot: on the ground 0.68 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.20 | -0.125 | no | yes | 0.65, 3.80
0.20 | -0.07 | 1.19 | -0.385 | no | yes | 1.26, 4.40
0.30 | -0.12 | 1.18 | -0.538 | no | yes | 1.91, 5.05
0.40 | -0.17 | 1.18 | -0.459 | no | yes | 2.51, 5.65
0.50 | -0.17 | 1.21 | -0.252 | no | yes | 3.17, 0.03
0.60 | -0.12 | 1.19 | -0.214 | no | yes | 3.77, 0.63
0.70 | -0.14 | 1.01 | -0.574 | yes | no | 4.42, 1.28

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
kneeR: 0.00
footR: 0.00
thighL: 0.00
kneeL: 0.00
footL: 0.00
balance: 0.00

## Round 1: your reply

Round 0 fell backward within 0.8 s: the torso pitched back to about -0.64 rad and the knees collapsed (right leg down to -2.67 rad). This revision makes four changes:
- Stronger torso-angle and angular-velocity feedback on the thighs.
- Knee and ankle stiffness terms that hold the joints near straight.
- Smaller rhythmic amplitudes.
- Everything else unchanged.

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
 "bias": {"a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.3}, "range": 1.0, "tol": 0.01, "to": {"a0": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(R)": -0.4, "obs[3]": -1.5, "obs[12]": -0.05}, "range": 6.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05}, "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.3}, "range": 1.0, "tol": 0.01, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(L)": -0.4, "obs[6]": -1.5, "obs[15]": -0.05}, "range": 6.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05}, "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[10]": -0.4}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.92 | 1.71 | height too low
1 | -0.92 | 1.66 | height too low
2 | -0.96 | 1.59 | height too low
3 | -0.96 | 1.54 | height too low
4 | -0.97 | 1.62 | height too low
5 | -0.95 | 1.55 | height too low
6 | -0.95 | 1.58 | height too low
7 | -0.96 | 1.58 | height too low
8 | -0.92 | 1.70 | height too low
9 | -0.93 | 1.69 | height too low

Over the 10 episodes: mean d -0.94 m, min -0.97, max -0.92; mean time survived 1.62 s; mean forward speed -0.58 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.034 | 0.035 | 0.61 | 0.36
right leg | -0.156 | 0.011 | 0.19 | 0.00
right foot | -0.054 | 0.056 | 0.04 | 0.00
left thigh | -0.069 | 0.033 | 0.58 | 0.25
left leg | -0.113 | 0.008 | 0.24 | 0.00
left foot | -0.064 | 0.013 | 0.03 | 0.00
torso angle min -0.851, max -0.004 rad; torso height min 0.80, max 1.25 m
right foot: on the ground 0.94 of the steps, 1 touchdowns
left foot: on the ground 0.94 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.018 | yes | yes | 0.65, 3.80
0.20 | -0.01 | 1.21 | -0.057 | yes | yes | 1.26, 4.40
0.30 | -0.03 | 1.21 | -0.082 | yes | yes | 1.91, 5.05
0.40 | -0.04 | 1.21 | -0.078 | yes | yes | 2.51, 5.65
0.50 | -0.05 | 1.21 | -0.044 | yes | yes | 3.17, 0.03
0.60 | -0.07 | 1.21 | -0.058 | yes | yes | 3.77, 0.63
0.70 | -0.09 | 1.20 | -0.100 | yes | yes | 4.42, 1.28
0.80 | -0.11 | 1.20 | -0.128 | yes | yes | 5.03, 1.88
0.90 | -0.13 | 1.20 | -0.123 | yes | yes | 5.68, 2.54
1.00 | -0.16 | 1.20 | -0.129 | yes | yes | 0.00, 3.14
1.10 | -0.20 | 1.19 | -0.161 | yes | yes | 0.65, 3.80
1.20 | -0.26 | 1.18 | -0.211 | yes | yes | 1.26, 4.40
1.30 | -0.33 | 1.16 | -0.276 | yes | yes | 1.91, 5.05
1.40 | -0.43 | 1.13 | -0.355 | yes | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
kneeR: 0.00
footR: 0.00
thighL: 0.00
kneeL: 0.00
footL: 0.00
balance: 0.00

## Round 2: your reply

Round 1 never walked: both feet stayed on the ground and the torso slowly tipped backward. The thigh joints are limited to angles ≤ 0, so the positive half of the thigh and balance torques only pushed on the joint limit. I couldn't test any of this, so the ankle sign is a guess from the stated conventions.

Changes in this design:
- **Ankle balance:** the feet now get torque from the torso angle and angular velocity. The sign is derived by analogy with the thigh rule you gave.
- **Forward lean:** a small constant positive thigh bias leans the torso forward.
- **Gait:** larger thigh swing and weaker knee stiffness so the legs actually step.

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
 "bias": {"a0": 0.2, "a3": 0.2, "a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.6}, "range": 1.0, "tol": 0.01, "to": {"a0": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(R)": -0.6, "obs[3]": -0.5, "obs[12]": -0.03}, "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -0.5, "obs[1]": -2.0, "obs[10]": -0.2}, "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.6}, "range": 1.0, "tol": 0.01, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(L)": -0.6, "obs[6]": -0.5, "obs[15]": -0.03}, "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -0.5, "obs[1]": -2.0, "obs[10]": -0.2}, "range": 4.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[10]": -0.4}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.74 | 1.33 | height too low
1 | 0.75 | 1.39 | height too low
2 | 0.82 | 1.30 | height too low
3 | 0.75 | 1.33 | height too low
4 | 0.79 | 1.37 | height too low
5 | 0.73 | 1.30 | height too low
6 | 0.83 | 1.40 | height too low
7 | 0.79 | 1.36 | height too low
8 | 0.79 | 1.45 | height too low
9 | 0.75 | 1.37 | height too low

Over the 10 episodes: mean d 0.78 m, min 0.73, max 0.83; mean time survived 1.36 s; mean forward speed 0.57 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.764 | 0.031 | 0.72 | 0.53
right leg | -1.122 | 0.107 | 0.25 | 0.00
right foot | -0.028 | 0.930 | 0.44 | 0.25
left thigh | -1.061 | 0.038 | 0.66 | 0.54
left leg | -0.851 | 0.053 | 0.36 | 0.00
left foot | -0.028 | 0.852 | 0.44 | 0.25
torso angle min -0.143, max 0.130 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.40 of the steps, 9 touchdowns
left foot: on the ground 0.68 of the steps, 8 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.028 | yes | yes | 0.65, 3.80
0.20 | 0.01 | 1.20 | -0.104 | no | yes | 1.26, 4.40
0.30 | 0.02 | 1.20 | -0.119 | yes | yes | 1.91, 5.05
0.40 | 0.05 | 1.20 | -0.070 | no | yes | 2.51, 5.65
0.50 | 0.10 | 1.21 | 0.041 | no | no | 3.17, 0.03
0.60 | 0.15 | 1.20 | 0.095 | no | yes | 3.77, 0.63
0.70 | 0.13 | 1.15 | -0.065 | no | yes | 4.42, 1.28
0.80 | 0.15 | 1.12 | -0.126 | yes | yes | 5.03, 1.88
0.90 | 0.24 | 1.09 | -0.082 | yes | yes | 5.68, 2.54
1.00 | 0.35 | 1.08 | -0.051 | no | no | 0.00, 3.14
1.10 | 0.47 | 1.07 | -0.128 | no | no | 0.65, 3.80
1.20 | 0.58 | 1.00 | -0.077 | no | no | 1.26, 4.40
1.30 | 0.71 | 0.84 | -0.064 | yes | yes | 1.91, 5.05

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
kneeR: 0.00
footR: 0.00
thighL: 0.00
kneeL: 0.00
footL: 0.00
balance: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
