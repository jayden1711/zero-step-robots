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

This is my round-0 design: two antiphase oscillators at 1.2 Hz drive each leg's thigh, knee and foot, and torso-angle and angular-velocity feedback is added to both thighs. I haven't been able to test it, so the gains are initial guesses to revise from the practice results.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.6, "obs[1]": -0.8, "obs[10]": -0.2},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.7},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.3, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.6, "obs[1]": -0.8, "obs[10]": -0.2},
   "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.7},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.3, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.04 | 0.66 | height too low
1 | -0.05 | 0.66 | height too low
2 | -0.04 | 0.65 | height too low
3 | -0.06 | 0.65 | height too low
4 | -0.05 | 0.65 | height too low
5 | -0.03 | 0.66 | height too low
6 | -0.07 | 0.65 | height too low
7 | -0.02 | 0.66 | height too low
8 | -0.03 | 0.66 | height too low
9 | -0.05 | 0.66 | height too low

Over the 10 episodes: mean d -0.04 m, min -0.07, max -0.02; mean time survived 0.65 s; mean forward speed -0.07 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.380 | 0.033 | 0.56 | 0.27
right leg | -2.739 | 0.003 | 0.45 | 0.00
right foot | -0.998 | 0.986 | 0.16 | 0.00
left thigh | -0.597 | 0.044 | 0.35 | 0.06
left leg | -2.794 | 0.014 | 0.45 | 0.00
left foot | -0.264 | 0.913 | 0.25 | 0.00
torso angle min -0.569, max -0.005 rad; torso height min 0.80, max 1.27 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.40 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.04 | 1.21 | -0.200 | no | yes | 0.78, 3.93
0.20 | -0.12 | 1.17 | -0.502 | no | yes | 1.51, 4.65
0.30 | -0.16 | 1.19 | -0.535 | no | no | 2.29, 5.43
0.40 | -0.13 | 1.27 | -0.404 | no | no | 3.02, 6.16
0.50 | -0.13 | 1.23 | -0.276 | no | no | 3.80, 0.66
0.60 | -0.12 | 0.96 | -0.295 | no | no | 4.52, 1.38

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
r_knee: 0.00
r_foot: 0.00
l_thigh: 0.00
l_knee: 0.00
l_foot: 0.00

## Round 1: your reply

Round 0 pitched the torso backward within 0.2 s, so the robot fell with the torso at about -0.5 rad. My guess is that the swing/stance thigh torque (0.6) was too large and the knees flexed to their limit (about -2.7 rad). For this revision I'm reducing the thigh and knee amplitudes, adding a constant extension bias to both knees, strengthening the torso feedback, and slowing the gait to 1.0 Hz.

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
 "bias": {"a1": 0.3, "a4": 0.3},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.3, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.4},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.3, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.4},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.68 | 1.51 | height too low
1 | 0.81 | 1.30 | height too low
2 | 0.76 | 1.26 | height too low
3 | 0.85 | 1.31 | height too low
4 | 0.76 | 1.28 | height too low
5 | 0.80 | 1.25 | height too low
6 | 0.68 | 1.41 | height too low
7 | 0.84 | 1.19 | height too low
8 | 0.60 | 1.47 | height too low
9 | 0.72 | 1.58 | height too low

Over the 10 episodes: mean d 0.75 m, min 0.60, max 0.85; mean time survived 1.36 s; mean forward speed 0.56 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.337 | 0.022 | 0.60 | 0.38
right leg | -1.743 | 0.080 | 0.25 | 0.00
right foot | 0.004 | 0.874 | 0.06 | 0.00
left thigh | -1.041 | 0.030 | 0.54 | 0.38
left leg | -0.615 | 0.124 | 0.40 | 0.00
left foot | -0.186 | 0.877 | 0.07 | 0.00
torso angle min -0.183, max 0.111 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.72 of the steps, 7 touchdowns
left foot: on the ground 0.78 of the steps, 8 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.014 | yes | yes | 0.65, 3.80
0.20 | -0.02 | 1.21 | -0.061 | yes | yes | 1.26, 4.40
0.30 | -0.04 | 1.20 | -0.162 | no | yes | 1.91, 5.05
0.40 | -0.04 | 1.20 | -0.173 | no | yes | 2.51, 5.65
0.50 | -0.00 | 1.21 | -0.097 | yes | yes | 3.17, 0.03
0.60 | 0.01 | 1.21 | 0.038 | yes | yes | 3.77, 0.63
0.70 | 0.01 | 1.21 | -0.042 | yes | yes | 4.42, 1.28
0.80 | -0.01 | 1.20 | -0.137 | yes | no | 5.03, 1.88
0.90 | 0.03 | 1.19 | -0.154 | yes | no | 5.68, 2.54
1.00 | 0.09 | 1.18 | -0.087 | yes | yes | 0.00, 3.14
1.10 | 0.19 | 1.16 | 0.041 | yes | yes | 0.65, 3.80
1.20 | 0.27 | 1.13 | 0.110 | no | yes | 1.26, 4.40
1.30 | 0.37 | 1.07 | 0.026 | yes | no | 1.91, 5.05
1.40 | 0.49 | 0.97 | -0.051 | yes | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
r_knee: 0.00
r_foot: 0.00
l_thigh: 0.00
l_knee: 0.00
l_foot: 0.00

## Round 2: your reply

Round 1 survived about 1.4 s but barely moved forward (0.5 m in 1.4 s), and the legs buckled at the end. For round 2 I'm raising the knee extension bias and swing flexion, and adding a small forward thigh bias to produce forward lean and push. I'm also reducing the torso feedback gains, since the thigh actions were saturating 38% of the time.

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
 "bias": {"a0": 0.1, "a3": 0.1, "a1": 0.4, "a4": 0.4},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.4, "obs[1]": -1.0, "obs[10]": -0.15},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.5},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.4, "obs[1]": -1.0, "obs[10]": -0.15},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.5},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.01 | 2.02 | height too low
1 | -0.97 | 1.85 | height too low
2 | 0.88 | 2.90 | height too low
3 | -1.00 | 2.30 | height too low
4 | -1.05 | 2.98 | height too low
5 | -1.02 | 2.58 | height too low
6 | -1.05 | 1.97 | height too low
7 | -0.99 | 2.69 | height too low
8 | -1.06 | 1.95 | height too low
9 | -1.03 | 1.98 | height too low

Over the 10 episodes: mean d -0.83 m, min -1.06, max 0.88; mean time survived 2.32 s; mean forward speed -0.39 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.279 | 0.025 | 0.41 | 0.03
right leg | -0.592 | 0.101 | 0.42 | 0.00
right foot | -0.412 | 0.883 | 0.09 | 0.00
left thigh | -0.324 | 0.031 | 0.40 | 0.16
left leg | -0.672 | 0.103 | 0.42 | 0.00
left foot | -0.198 | 0.890 | 0.10 | 0.00
torso angle min -0.833, max -0.001 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.67 of the steps, 6 touchdowns
left foot: on the ground 0.74 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.012 | yes | yes | 0.65, 3.80
0.20 | -0.02 | 1.21 | -0.054 | yes | yes | 1.26, 4.40
0.30 | -0.06 | 1.20 | -0.232 | no | yes | 1.91, 5.05
0.40 | -0.05 | 1.20 | -0.266 | no | yes | 2.51, 5.65
0.50 | 0.00 | 1.21 | -0.092 | yes | yes | 3.17, 0.03
0.60 | 0.01 | 1.21 | -0.015 | yes | yes | 3.77, 0.63
0.70 | -0.03 | 1.20 | -0.130 | yes | no | 4.42, 1.28
0.80 | -0.07 | 1.20 | -0.275 | yes | no | 5.03, 1.88
0.90 | -0.07 | 1.20 | -0.273 | yes | no | 5.68, 2.54
1.00 | -0.04 | 1.21 | -0.102 | yes | yes | 0.00, 3.14
1.10 | -0.06 | 1.20 | -0.075 | yes | yes | 0.65, 3.80
1.20 | -0.11 | 1.20 | -0.175 | yes | yes | 1.26, 4.40
1.30 | -0.17 | 1.18 | -0.301 | no | yes | 1.91, 5.05
1.40 | -0.21 | 1.18 | -0.298 | no | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
r_knee: 0.00
r_foot: 0.00
l_thigh: 0.00
l_knee: 0.00
l_foot: 0.00

## Round 3: your reply

Round 2 got worse than round 1: the torso pitched backward and the robot walked in reverse, so I'm going back to the round-1 structure. From there I'm making only modest changes. The swing knee flexion and thigh drive are a bit larger so the feet actually leave the ground. The knee extension bias is slightly higher to stop the legs buckling. The angular-velocity feedback is reduced, since it was saturating the thigh actions.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.1, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.1, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.35, "a4": 0.35},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.4, "obs[1]": -1.5, "obs[10]": -0.2},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.6},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.4, "obs[1]": -1.5, "obs[10]": -0.2},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.6},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.54 | 0.97 | height too low
1 | 0.56 | 0.98 | height too low
2 | 0.52 | 0.93 | height too low
3 | 0.51 | 0.94 | height too low
4 | 0.52 | 0.94 | height too low
5 | 0.53 | 0.94 | height too low
6 | 0.52 | 0.96 | height too low
7 | 0.55 | 0.94 | height too low
8 | 0.55 | 0.96 | height too low
9 | 0.52 | 0.96 | height too low

Over the 10 episodes: mean d 0.53 m, min 0.51, max 0.56; mean time survived 0.95 s; mean forward speed 0.56 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.125 | 0.032 | 0.37 | 0.13
right leg | -1.082 | 0.230 | 0.43 | 0.00
right foot | -0.030 | 0.861 | 0.08 | 0.00
left thigh | -0.428 | 0.053 | 0.33 | 0.09
left leg | -1.706 | 0.016 | 0.45 | 0.00
left foot | -0.186 | 0.885 | 0.09 | 0.00
torso angle min -0.368, max -0.004 rad; torso height min 0.80, max 1.25 m
right foot: on the ground 0.50 of the steps, 2 touchdowns
left foot: on the ground 0.60 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.018 | yes | yes | 0.72, 3.86
0.20 | -0.04 | 1.20 | -0.170 | no | yes | 1.38, 4.52
0.30 | -0.07 | 1.19 | -0.358 | no | yes | 2.10, 5.24
0.40 | -0.04 | 1.20 | -0.312 | no | yes | 2.76, 5.91
0.50 | 0.05 | 1.20 | -0.155 | no | yes | 3.48, 0.34
0.60 | 0.07 | 1.18 | -0.073 | yes | no | 4.15, 1.01
0.70 | 0.08 | 1.09 | -0.306 | yes | no | 4.87, 1.72
0.80 | 0.21 | 1.03 | -0.288 | yes | no | 5.53, 2.39
0.90 | 0.41 | 0.90 | -0.159 | yes | no | 6.25, 3.11

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
r_knee: 0.00
r_foot: 0.00
l_thigh: 0.00
l_knee: 0.00
l_foot: 0.00

## Round 4: your reply

Round 1 was the best design so far (0.75 m, 1.36 s), so I'm keeping its structure and changing only the knee. Both knee biases go up from 0.3 to 0.45 to stop the legs buckling, and the swing flexion amplitude stays at 0.4. Rounds 2 and 3 showed that larger thigh drive or knee amplitude made things worse.

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
 "bias": {"a1": 0.45, "a4": 0.45},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.3, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.4},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.3, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.4},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 4: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.99 | 1.72 | height too low
1 | -1.15 | 1.50 | height too low
2 | -1.17 | 1.58 | height too low
3 | -1.09 | 2.04 | height too low
4 | -1.24 | 3.53 | height too low
5 | -1.26 | 2.95 | height too low
6 | -1.17 | 1.54 | height too low
7 | -1.06 | 1.50 | height too low
8 | -1.00 | 1.78 | height too low
9 | -1.00 | 1.72 | height too low

Over the 10 episodes: mean d -1.11 m, min -1.26, max -0.99; mean time survived 1.99 s; mean forward speed -0.60 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.044 | 0.027 | 0.47 | 0.15
right leg | -0.087 | 0.022 | 0.41 | 0.00
right foot | -0.192 | 0.884 | 0.07 | 0.00
left thigh | -0.116 | 0.034 | 0.40 | 0.14
left leg | -0.306 | 0.053 | 0.49 | 0.00
left foot | -0.233 | 0.877 | 0.10 | 0.00
torso angle min -0.828, max -0.004 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.86 of the steps, 5 touchdowns
left foot: on the ground 0.94 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.009 | yes | yes | 0.65, 3.80
0.20 | -0.01 | 1.21 | -0.022 | yes | yes | 1.26, 4.40
0.30 | -0.03 | 1.21 | -0.067 | yes | yes | 1.91, 5.05
0.40 | -0.03 | 1.21 | -0.061 | yes | yes | 2.51, 5.65
0.50 | -0.04 | 1.21 | -0.080 | yes | yes | 3.17, 0.03
0.60 | -0.06 | 1.20 | -0.093 | yes | yes | 3.77, 0.63
0.70 | -0.09 | 1.20 | -0.119 | yes | yes | 4.42, 1.28
0.80 | -0.12 | 1.19 | -0.177 | yes | yes | 5.03, 1.88
0.90 | -0.13 | 1.20 | -0.147 | yes | yes | 5.68, 2.54
1.00 | -0.14 | 1.20 | -0.102 | yes | yes | 0.00, 3.14
1.10 | -0.19 | 1.19 | -0.139 | yes | yes | 0.65, 3.80
1.20 | -0.26 | 1.18 | -0.199 | yes | yes | 1.26, 4.40
1.30 | -0.35 | 1.16 | -0.270 | yes | yes | 1.91, 5.05
1.40 | -0.44 | 1.14 | -0.322 | no | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
r_knee: 0.00
r_foot: 0.00
l_thigh: 0.00
l_knee: 0.00
l_foot: 0.00

## Now: round 5 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). This is the last round: this design is final and is the one scored. You may resubmit an earlier design unchanged by copying
its spec.
