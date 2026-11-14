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

This is my round-0 design: two antiphase oscillators, one per leg. Each drives a thigh with a sine, a knee that flexes during swing, and torso-angle and angular-velocity feedback on both thighs. I haven't run it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": -0.15, "a4": -0.15},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"obs[1]": -2.0, "obs[10]": -0.2, "sin(R)": 0.5},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"obs[1]": -2.0, "obs[10]": -0.2, "sin(L)": 0.5},
   "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": -0.2,
   "sharpness": 5.0, "to": {"a1": -0.45}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": -0.2,
   "sharpness": 5.0, "to": {"a4": -0.45}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.21 | 0.18 | height too low
1 | -0.21 | 0.17 | torso angle out of range
2 | -0.22 | 0.18 | height too low
3 | -0.22 | 0.18 | height too low
4 | -0.22 | 0.18 | height too low
5 | -0.22 | 0.18 | height too low
6 | -0.22 | 0.18 | height too low
7 | -0.22 | 0.18 | height too low
8 | -0.22 | 0.18 | height too low
9 | -0.22 | 0.18 | height too low

Over the 10 episodes: mean d -0.22 m, min -0.22, max -0.21; mean time survived 0.18 s; mean forward speed -1.23 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.005 | 0.037 | 0.89 | 0.82
right leg | -2.393 | 0.003 | 0.59 | 0.00
right foot | -0.138 | 0.165 | 0.00 | 0.00
left thigh | 0.001 | 0.019 | 0.88 | 0.77
left leg | -1.802 | 0.002 | 0.26 | 0.00
left foot | 0.000 | 0.487 | 0.00 | 0.00
torso angle min -0.999, max -0.005 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.05 of the steps, 1 touchdowns
left foot: on the ground 0.23 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.14 | 1.10 | -0.560 | no | no | 0.65, 3.80

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.32
thighL: 0.00

## Round 1: your reply

Round 0 fell within 0.2 s, and the logs point to the knees buckling. The knee reflex plus bias gave about -0.5 torque at start, and the right knee reached -2.39 rad. This revision keeps the knees pushed straight in stance and flexes them only briefly in swing. It also halves the thigh feedback gains so the thigh unit stops saturating. I haven't run it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"obs[1]": -1.0, "obs[10]": -0.1, "sin(R)": 0.4},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"obs[1]": -1.0, "obs[10]": -0.1, "sin(L)": 0.4},
   "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a1": -0.25}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a4": -0.25}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.36 | 0.94 | height too low
1 | 0.36 | 0.94 | height too low
2 | 0.28 | 0.88 | height too low
3 | 0.32 | 0.90 | height too low
4 | 0.30 | 0.90 | height too low
5 | 0.30 | 0.89 | height too low
6 | 0.35 | 0.94 | height too low
7 | 0.30 | 0.89 | height too low
8 | 0.35 | 0.92 | height too low
9 | 0.36 | 0.94 | height too low

Over the 10 episodes: mean d 0.33 m, min 0.28, max 0.36; mean time survived 0.91 s; mean forward speed 0.36 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.350 | 0.028 | 0.41 | 0.09
right leg | -1.190 | 0.198 | 0.24 | 0.00
right foot | -0.305 | 0.848 | 0.00 | 0.00
left thigh | -0.575 | 0.052 | 0.37 | 0.08
left leg | -1.937 | 0.008 | 0.25 | 0.00
left foot | -0.000 | 0.796 | 0.00 | 0.00
torso angle min -0.550, max -0.003 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.44 of the steps, 9 touchdowns
left foot: on the ground 0.84 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.025 | yes | yes | 0.65, 3.80
0.20 | -0.05 | 1.20 | -0.262 | yes | yes | 1.26, 4.40
0.30 | -0.08 | 1.18 | -0.497 | no | yes | 1.91, 5.05
0.40 | -0.08 | 1.18 | -0.544 | no | yes | 2.51, 5.65
0.50 | -0.02 | 1.19 | -0.351 | yes | yes | 3.17, 0.03
0.60 | 0.08 | 1.20 | -0.107 | no | yes | 3.77, 0.63
0.70 | 0.06 | 1.11 | -0.326 | yes | yes | 4.42, 1.28
0.80 | 0.11 | 0.98 | -0.486 | yes | yes | 5.03, 1.88
0.90 | 0.29 | 0.85 | -0.414 | yes | yes | 5.68, 2.54

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00

## Round 2: your reply

Round 1 survived about 0.9 s, but the torso pitched backward to -0.55 rad and the legs then collapsed. I'm raising the torso-feedback gains on the thighs, shrinking the rhythmic thigh swing so it disturbs the torso less, and adding a small positive thigh bias for a slight forward lean. I'm also stiffening the knees in stance. I haven't run it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.1, "a3": 0.1, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3, "sin(R)": 0.25},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3, "sin(L)": 0.25},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a1": -0.4}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a4": -0.4}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.80 | 1.61 | height too low
1 | 0.39 | 2.86 | height too low
2 | 0.73 | 1.46 | height too low
3 | 0.76 | 1.50 | height too low
4 | 0.72 | 1.43 | height too low
5 | 0.75 | 1.53 | height too low
6 | 0.82 | 1.70 | height too low
7 | 0.69 | 1.57 | height too low
8 | 0.51 | 1.78 | height too low
9 | 0.43 | 1.80 | height too low

Over the 10 episodes: mean d 0.66 m, min 0.39, max 0.82; mean time survived 1.72 s; mean forward speed 0.41 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.047 | 0.033 | 0.61 | 0.23
right leg | -1.474 | 0.124 | 0.35 | 0.00
right foot | -0.829 | 0.326 | 0.00 | 0.00
left thigh | -1.075 | 0.034 | 0.53 | 0.20
left leg | -0.412 | 0.117 | 0.45 | 0.00
left foot | -0.001 | 0.706 | 0.00 | 0.00
torso angle min -0.155, max 0.115 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.46 of the steps, 18 touchdowns
left foot: on the ground 0.86 of the steps, 5 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | 0.00 | 1.20 | -0.006 | yes | yes | 0.65, 3.80
0.20 | -0.02 | 1.21 | -0.091 | no | yes | 1.26, 4.40
0.30 | -0.03 | 1.20 | -0.142 | no | yes | 1.91, 5.05
0.40 | -0.02 | 1.20 | -0.134 | no | yes | 2.51, 5.65
0.50 | 0.01 | 1.21 | -0.060 | no | yes | 3.17, 0.03
0.60 | 0.01 | 1.21 | -0.016 | no | yes | 3.77, 0.63
0.70 | -0.02 | 1.19 | -0.130 | yes | yes | 4.42, 1.28
0.80 | -0.02 | 1.19 | -0.155 | yes | yes | 5.03, 1.88
0.90 | 0.01 | 1.19 | -0.145 | yes | yes | 5.68, 2.54
1.00 | 0.07 | 1.19 | -0.074 | yes | yes | 0.00, 3.14
1.10 | 0.16 | 1.20 | 0.067 | yes | no | 0.65, 3.80
1.20 | 0.20 | 1.17 | 0.031 | no | yes | 1.26, 4.40
1.30 | 0.26 | 1.15 | -0.103 | no | yes | 1.91, 5.05
1.40 | 0.38 | 1.10 | -0.083 | no | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
