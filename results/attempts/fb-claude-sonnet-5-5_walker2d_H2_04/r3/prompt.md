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

This is the round-0 design: two antiphase oscillators at 1 Hz, with a thigh, knee and foot unit per leg. The thighs get PD feedback on torso angle and angular velocity, and each knee flexes during swing. I have not run it, so the gains are untuned starting values.

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
 "bias": {},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.6, "obs[1]": -1.0, "obs[10]": -0.2},
   "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.6, "obs[1]": -1.0, "obs[10]": -0.2},
   "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.6},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.6},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"obs[4]": -0.3, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"obs[7]": -0.3, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.06 | 0.78 | height too low
1 | 0.05 | 0.78 | height too low
2 | 0.10 | 0.78 | height too low
3 | 0.08 | 0.78 | height too low
4 | 0.07 | 0.78 | height too low
5 | 0.08 | 0.78 | height too low
6 | 0.06 | 0.78 | height too low
7 | 0.09 | 0.78 | height too low
8 | 0.07 | 0.78 | height too low
9 | 0.06 | 0.78 | height too low

Over the 10 episodes: mean d 0.07 m, min 0.05, max 0.10; mean time survived 0.78 s; mean forward speed 0.09 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -2.346 | 0.037 | 0.60 | 0.31
right leg | -2.700 | 0.286 | 0.38 | 0.00
right foot | -0.366 | 0.157 | 0.08 | 0.00
left thigh | -0.722 | 0.087 | 0.42 | 0.20
left leg | -2.550 | 0.009 | 0.38 | 0.00
left foot | -0.028 | 0.294 | 0.04 | 0.00
torso angle min -0.720, max -0.005 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.08 of the steps, 1 touchdowns
left foot: on the ground 0.54 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.20 | -0.126 | yes | yes | 0.65, 3.80
0.20 | -0.09 | 1.18 | -0.453 | no | yes | 1.26, 4.40
0.30 | -0.12 | 1.16 | -0.711 | no | yes | 1.91, 5.05
0.40 | -0.13 | 1.17 | -0.623 | no | yes | 2.51, 5.65
0.50 | -0.06 | 1.21 | -0.366 | no | no | 3.17, 0.03
0.60 | -0.02 | 1.19 | -0.228 | no | yes | 3.77, 0.63
0.70 | 0.02 | 1.03 | -0.576 | no | no | 4.42, 1.28

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
l_thigh: 0.00
r_knee: 0.00
l_knee: 0.00
r_foot: 0.00
l_foot: 0.00

## Round 1: your reply

Round 0 fell at about 0.8 s with the torso pitching backward, and both knees collapsed. This revision lowers the rhythmic amplitudes, doubles the torso-angle feedback on the thighs, and adds knee and ankle stiffness plus a small extension bias on the knees.

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
 "bias": {"a1": 0.15, "a4": 0.15},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.35, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.35, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.4, "obs[3]": -0.8, "obs[12]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.4, "obs[6]": -0.8, "obs[15]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"obs[4]": -0.5, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"obs[7]": -0.5, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.92 | 1.67 | height too low
1 | -0.92 | 1.65 | height too low
2 | -0.93 | 1.74 | height too low
3 | -0.93 | 1.73 | height too low
4 | -0.94 | 1.78 | height too low
5 | -0.93 | 1.78 | height too low
6 | -0.93 | 1.67 | height too low
7 | -0.93 | 1.70 | height too low
8 | -0.92 | 1.70 | height too low
9 | -0.92 | 1.67 | height too low

Over the 10 episodes: mean d -0.93 m, min -0.94, max -0.92; mean time survived 1.71 s; mean forward speed -0.54 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.133 | 0.033 | 0.64 | 0.40
right leg | -0.254 | 0.025 | 0.20 | 0.00
right foot | -0.086 | 0.077 | 0.04 | 0.00
left thigh | -0.129 | 0.029 | 0.49 | 0.25
left leg | -0.237 | 0.015 | 0.28 | 0.00
left foot | -0.118 | 0.014 | 0.03 | 0.00
torso angle min -0.841, max -0.004 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.94 of the steps, 1 touchdowns
left foot: on the ground 0.93 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.017 | yes | yes | 0.65, 3.80
0.20 | -0.02 | 1.21 | -0.079 | yes | yes | 1.26, 4.40
0.30 | -0.04 | 1.20 | -0.134 | yes | yes | 1.91, 5.05
0.40 | -0.05 | 1.20 | -0.131 | yes | yes | 2.51, 5.65
0.50 | -0.05 | 1.21 | -0.076 | yes | yes | 3.17, 0.03
0.60 | -0.07 | 1.21 | -0.134 | yes | yes | 3.77, 0.63
0.70 | -0.09 | 1.20 | -0.164 | yes | yes | 4.42, 1.28
0.80 | -0.12 | 1.20 | -0.192 | yes | yes | 5.03, 1.88
0.90 | -0.15 | 1.20 | -0.186 | yes | yes | 5.68, 2.54
1.00 | -0.17 | 1.20 | -0.140 | yes | yes | 0.00, 3.14
1.10 | -0.22 | 1.19 | -0.177 | yes | yes | 0.65, 3.80
1.20 | -0.28 | 1.17 | -0.236 | yes | yes | 1.26, 4.40
1.30 | -0.37 | 1.15 | -0.313 | yes | yes | 1.91, 5.05
1.40 | -0.47 | 1.11 | -0.398 | yes | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
l_thigh: 0.00
r_knee: 0.00
l_knee: 0.00
r_foot: 0.00
l_foot: 0.00

## Round 2: your reply

Round 1 stood on both feet with stiff legs and slowly tipped over backwards. The thighs were already at their joint limit (angle 0), so the hip feedback could do nothing. This revision adds ankle torque feedback on torso angle, because a positive foot torque with the foot planted pitches the body forward. It also deepens the knee flexion during swing and adds a small forward-lean bias at the feet. I have not run it.

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
 "bias": {"a1": 0.1, "a4": 0.1, "a2": 0.1, "a5": 0.1},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.5, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.5, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.6, "obs[3]": -0.5, "obs[12]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.6, "obs[6]": -0.5, "obs[15]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"obs[4]": -0.3, "obs[13]": -0.03, "obs[1]": -1.5, "obs[10]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"obs[7]": -0.3, "obs[16]": -0.03, "obs[1]": -1.5, "obs[10]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 1.11 | 1.19 | height too low
1 | 1.08 | 1.20 | height too low
2 | 0.82 | 1.00 | height too low
3 | 0.97 | 1.10 | height too low
4 | 0.80 | 0.96 | height too low
5 | 0.84 | 1.06 | height too low
6 | 1.04 | 1.17 | height too low
7 | 0.80 | 0.95 | height too low
8 | 0.95 | 1.08 | height too low
9 | 1.05 | 1.18 | height too low

Over the 10 episodes: mean d 0.95 m, min 0.80, max 1.11; mean time survived 1.09 s; mean forward speed 0.87 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.953 | 0.026 | 0.85 | 0.64
right leg | -0.789 | 0.065 | 0.26 | 0.00
right foot | 0.004 | 0.833 | 0.58 | 0.27
left thigh | -1.165 | 0.001 | 0.63 | 0.47
left leg | -0.838 | 0.082 | 0.33 | 0.00
left foot | 0.000 | 0.851 | 0.58 | 0.22
torso angle min -0.209, max -0.003 rad; torso height min 0.80, max 1.25 m
right foot: on the ground 0.34 of the steps, 10 touchdowns
left foot: on the ground 0.52 of the steps, 6 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.045 | yes | yes | 0.65, 3.80
0.20 | -0.00 | 1.20 | -0.149 | no | yes | 1.26, 4.40
0.30 | 0.01 | 1.20 | -0.207 | no | yes | 1.91, 5.05
0.40 | 0.05 | 1.20 | -0.174 | no | yes | 2.51, 5.65
0.50 | 0.11 | 1.20 | -0.132 | no | yes | 3.17, 0.03
0.60 | 0.18 | 1.18 | -0.197 | yes | no | 3.77, 0.63
0.70 | 0.26 | 1.17 | -0.176 | yes | no | 4.42, 1.28
0.80 | 0.37 | 1.15 | -0.118 | no | no | 5.03, 1.88
0.90 | 0.53 | 1.09 | -0.087 | yes | yes | 5.68, 2.54
1.00 | 0.71 | 1.01 | -0.153 | no | yes | 0.00, 3.14
1.10 | 0.94 | 0.91 | -0.126 | yes | no | 0.65, 3.80

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
r_thigh: 0.00
l_thigh: 0.00
r_knee: 0.00
l_knee: 0.00
r_foot: 0.00
l_foot: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
