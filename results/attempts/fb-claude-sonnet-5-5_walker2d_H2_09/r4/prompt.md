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

This is the round-0 design. Each leg has its own oscillator, and the two are coupled half a cycle apart. For each leg:

- **Thigh:** driven by `sin(phase)`, so it swings forward in the first half of the cycle and back in the second. Torso angle and angular-velocity feedback is added on top.
- **Knee:** flexes through a reflex while the leg is in its forward-swing half and extends in its stance half.
- **Feet:** unactuated for now, to keep this first design simple.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 1.5, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 1.5, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.6, "obs[1]": -0.5, "obs[10]": -0.1},
   "range": 2.5, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.6, "obs[1]": -0.5, "obs[10]": -0.1},
   "range": 2.5, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a1": -0.6}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a4": -0.6}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.14 | 0.76 | height too low
1 | -0.03 | 0.70 | torso angle out of range
2 | 0.16 | 0.75 | height too low
3 | 0.17 | 0.76 | height too low
4 | 0.10 | 0.74 | height too low
5 | 0.11 | 0.74 | height too low
6 | 0.15 | 0.76 | height too low
7 | 0.11 | 0.74 | height too low
8 | 0.15 | 0.76 | height too low
9 | 0.14 | 0.76 | height too low

Over the 10 episodes: mean d 0.12 m, min -0.03, max 0.17; mean time survived 0.75 s; mean forward speed 0.16 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.783 | 0.030 | 0.61 | 0.26
right leg | -2.730 | 0.003 | 0.54 | 0.00
right foot | -0.862 | 0.166 | 0.00 | 0.00
left thigh | -0.993 | 0.110 | 0.34 | 0.14
left leg | -2.753 | 0.014 | 0.54 | 0.00
left foot | -0.900 | 0.395 | 0.00 | 0.00
torso angle min -0.997, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.12 of the steps, 2 touchdowns
left foot: on the ground 0.51 of the steps, 5 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.06 | 1.18 | -0.344 | no | yes | 0.65, 3.80
0.20 | -0.13 | 1.14 | -0.812 | no | yes | 1.26, 4.40
0.30 | -0.15 | 1.15 | -0.944 | no | yes | 1.91, 5.05
0.40 | -0.13 | 1.21 | -0.818 | no | no | 2.51, 5.65
0.50 | -0.12 | 1.16 | -0.723 | no | yes | 3.17, 0.03
0.60 | -0.08 | 1.11 | -0.500 | no | no | 3.77, 0.63
0.70 | 0.02 | 0.84 | -0.997 | yes | no | 4.42, 1.28

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00

## Round 1: your reply

Round 0 failed because the torso pitched backward within 0.3 s while both knees were driven into their flexion limit (about -2.7 rad), so the walker sat down and fell. For round 1 I'm making these changes:

- **Knees:** a positive bias plus a smaller flexion reflex, so the knees stay mostly extended and bend only moderately in swing.
- **Thighs:** stronger torso angle and angular-velocity feedback, and a small forward bias, to counter the backward pitch.
- **Feet:** a light stiffness and damping on the ankles so they stop flopping.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 1.5, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 1.5, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.1, "a3": 0.1, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.4, "obs[1]": -1.5, "obs[10]": -0.2},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.4, "obs[1]": -1.5, "obs[10]": -0.2},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -0.5, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -0.5, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.98 | 1.47 | height too low
1 | -1.02 | 1.47 | height too low
2 | -0.99 | 1.49 | height too low
3 | -0.98 | 1.47 | height too low
4 | -0.98 | 1.47 | height too low
5 | -0.98 | 1.47 | height too low
6 | -1.01 | 1.47 | height too low
7 | -1.00 | 1.48 | height too low
8 | -1.02 | 1.47 | height too low
9 | -0.99 | 1.46 | height too low

Over the 10 episodes: mean d -1.00 m, min -1.02, max -0.98; mean time survived 1.47 s; mean forward speed -0.68 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.167 | 0.085 | 0.71 | 0.38
right leg | -2.425 | 0.276 | 0.37 | 0.00
right foot | -0.248 | 0.323 | 0.08 | 0.00
left thigh | -0.394 | 0.051 | 0.60 | 0.36
left leg | -0.919 | 0.148 | 0.50 | 0.00
left foot | -0.182 | 0.331 | 0.08 | 0.00
torso angle min -0.822, max -0.002 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.33 of the steps, 3 touchdowns
left foot: on the ground 0.88 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.01 | 1.20 | -0.069 | yes | yes | 0.65, 3.80
0.20 | -0.06 | 1.20 | -0.258 | yes | yes | 1.26, 4.40
0.30 | -0.09 | 1.19 | -0.399 | no | yes | 1.91, 5.05
0.40 | -0.09 | 1.19 | -0.390 | no | yes | 2.51, 5.65
0.50 | -0.07 | 1.20 | -0.240 | no | yes | 3.17, 0.03
0.60 | 0.00 | 1.20 | -0.100 | no | yes | 3.77, 0.63
0.70 | -0.10 | 1.15 | -0.393 | no | yes | 4.42, 1.28
0.80 | -0.17 | 1.09 | -0.512 | yes | yes | 5.03, 1.88
0.90 | -0.23 | 1.07 | -0.583 | yes | yes | 5.68, 2.54
1.00 | -0.28 | 1.11 | -0.528 | yes | yes | 0.00, 3.14
1.10 | -0.33 | 1.18 | -0.220 | no | no | 0.65, 3.80
1.20 | -0.52 | 1.12 | -0.562 | no | yes | 1.26, 4.40
1.30 | -0.66 | 1.05 | -0.645 | no | yes | 1.91, 5.05
1.40 | -0.81 | 0.96 | -0.623 | no | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00
footR: 0.00
footL: 0.00

## Round 2: your reply

Round 1 still fell backward: the torso angle went to about -0.8 rad and the walker sat down. I'm strengthening the torso feedback on both thighs and shrinking the rhythmic thigh swing, so balance dominates over stepping. I'm also stiffening the ankles a little and keeping the knee settings.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 1.5, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 1.5, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.3, "a4": 0.3},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.3, "obs[1]": -3.0, "obs[10]": -0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.3, "obs[1]": -3.0, "obs[10]": -0.4},
   "range": 6.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -1.0, "obs[13]": -0.08},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -1.0, "obs[16]": -0.08},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.93 | 1.52 | height too low
1 | -0.91 | 1.42 | height too low
2 | -0.94 | 1.38 | height too low
3 | -0.92 | 1.43 | height too low
4 | -0.93 | 1.46 | height too low
5 | -0.93 | 1.37 | height too low
6 | -0.92 | 1.44 | height too low
7 | -0.93 | 1.37 | height too low
8 | -0.90 | 1.42 | height too low
9 | -0.92 | 1.45 | height too low

Over the 10 episodes: mean d -0.92 m, min -0.94, max -0.90; mean time survived 1.42 s; mean forward speed -0.65 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.101 | 0.033 | 0.74 | 0.38
right leg | -0.243 | 0.038 | 0.35 | 0.00
right foot | -0.058 | 0.073 | 0.05 | 0.00
left thigh | -0.098 | 0.033 | 0.72 | 0.36
left leg | -0.212 | 0.014 | 0.53 | 0.00
left foot | -0.071 | 0.006 | 0.04 | 0.00
torso angle min -0.842, max 0.000 rad; torso height min 0.80, max 1.25 m
right foot: on the ground 0.94 of the steps, 1 touchdowns
left foot: on the ground 0.90 of the steps, 5 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.016 | yes | yes | 0.65, 3.80
0.20 | -0.02 | 1.21 | -0.076 | yes | yes | 1.26, 4.40
0.30 | -0.04 | 1.20 | -0.120 | yes | yes | 1.91, 5.05
0.40 | -0.06 | 1.20 | -0.128 | yes | yes | 2.51, 5.65
0.50 | -0.07 | 1.20 | -0.079 | yes | yes | 3.17, 0.03
0.60 | -0.11 | 1.20 | -0.141 | yes | no | 3.77, 0.63
0.70 | -0.14 | 1.20 | -0.173 | yes | yes | 4.42, 1.28
0.80 | -0.17 | 1.19 | -0.174 | yes | yes | 5.03, 1.88
0.90 | -0.21 | 1.19 | -0.173 | yes | yes | 5.68, 2.54
1.00 | -0.26 | 1.18 | -0.201 | yes | yes | 0.00, 3.14
1.10 | -0.33 | 1.16 | -0.254 | yes | yes | 0.65, 3.80
1.20 | -0.43 | 1.13 | -0.338 | yes | yes | 1.26, 4.40
1.30 | -0.56 | 1.08 | -0.460 | yes | yes | 1.91, 5.05
1.40 | -0.72 | 0.99 | -0.610 | yes | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00
footR: 0.00
footL: 0.00

## Round 3: your reply

Round 2 fell backward with the legs held straight and the ankles passive, so the whole body tipped about the feet. This round I'm adding ankle feedback on torso angle and angular velocity, so a backward lean produces a negative foot torque that pushes the shin forward. A small negative ankle bias gives a slight forward lean, and the rest of the design stays as in round 2.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 1.5, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 1.5, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.3, "a4": 0.3, "a2": -0.2, "a5": -0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.3, "obs[1]": -3.0, "obs[10]": -0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.3, "obs[1]": -3.0, "obs[10]": -0.4},
   "range": 6.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "footR", "inputs": {"obs[1]": 3.0, "obs[10]": 0.4, "obs[4]": -0.5},
   "range": 6.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[1]": 3.0, "obs[10]": 0.4, "obs[7]": -0.5},
   "range": 6.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.60 | 0.44 | torso angle out of range
1 | -0.58 | 0.44 | torso angle out of range
2 | -0.59 | 0.54 | torso angle out of range
3 | -0.61 | 0.44 | torso angle out of range
4 | -0.63 | 0.46 | torso angle out of range
5 | -0.58 | 0.53 | torso angle out of range
6 | -0.61 | 0.44 | torso angle out of range
7 | -0.60 | 0.53 | torso angle out of range
8 | -0.60 | 0.45 | torso angle out of range
9 | -0.59 | 0.44 | torso angle out of range

Over the 10 episodes: mean d -0.60 m, min -0.63, max -0.58; mean time survived 0.47 s; mean forward speed -1.28 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.005 | 0.035 | 0.79 | 0.62
right leg | -0.765 | 0.008 | 0.17 | 0.00
right foot | -0.925 | 0.004 | 0.70 | 0.56
left thigh | 0.000 | 0.018 | 0.66 | 0.55
left leg | 0.002 | 0.023 | 0.74 | 0.00
left foot | -0.935 | 0.000 | 0.70 | 0.56
torso angle min -0.992, max -0.003 rad; torso height min 1.18, max 1.36 m
right foot: on the ground 0.42 of the steps, 1 touchdowns
left foot: on the ground 0.42 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.25 | -0.016 | yes | yes | 0.65, 3.80
0.20 | -0.11 | 1.28 | -0.108 | yes | yes | 1.26, 4.40
0.30 | -0.35 | 1.36 | -0.470 | no | no | 1.91, 5.05
0.40 | -0.55 | 1.25 | -0.852 | no | no | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00
footR: 0.00
footL: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
