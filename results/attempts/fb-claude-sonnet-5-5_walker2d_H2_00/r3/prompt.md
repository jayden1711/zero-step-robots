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

This is the round-0 design. The two oscillators are coupled in antiphase at 1 Hz. Each thigh is driven by its own oscillator's cosine. Each knee flexes through a reflex while that leg's thigh torque is positive (swing). The feet get a small rhythmic drive. Torso angle and angular velocity feed back to both thighs as negative gains. I have not simulated it, and the gait signs are a first guess to be adjusted from your results.

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
  {"type": "linear", "name": "thighR", "inputs": {"cos(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a0": 0.6}},
  {"type": "linear", "name": "thighL", "inputs": {"cos(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a3": 0.6}},
  {"type": "reflex", "name": "kneeR", "inputs": {"cos(R)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a1": -0.4}},
  {"type": "reflex", "name": "kneeL", "inputs": {"cos(L)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a4": -0.4}},
  {"type": "linear", "name": "footR", "inputs": {"sin(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "footL", "inputs": {"sin(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a5": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -1.0, "obs[10]": -0.1}, "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.03 | 0.51 | torso angle out of range
1 | -0.04 | 0.51 | torso angle out of range
2 | -0.01 | 0.52 | torso angle out of range
3 | -0.02 | 0.51 | torso angle out of range
4 | -0.02 | 0.51 | torso angle out of range
5 | -0.02 | 0.51 | torso angle out of range
6 | -0.03 | 0.51 | torso angle out of range
7 | -0.02 | 0.51 | torso angle out of range
8 | -0.02 | 0.51 | torso angle out of range
9 | -0.03 | 0.51 | torso angle out of range

Over the 10 episodes: mean d -0.02 m, min -0.04, max -0.01; mean time survived 0.51 s; mean forward speed -0.05 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -2.589 | 0.031 | 0.66 | 0.28
right leg | -2.670 | 0.025 | 0.36 | 0.00
right foot | 0.004 | 0.910 | 0.18 | 0.00
left thigh | -0.654 | 0.079 | 0.53 | 0.30
left leg | -1.892 | 0.008 | 0.36 | 0.00
left foot | -0.877 | 0.069 | 0.18 | 0.00
torso angle min -0.986, max -0.005 rad; torso height min 0.96, max 1.25 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.66 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.08 | 1.17 | -0.472 | no | yes | 0.65, 3.80
0.20 | -0.10 | 1.17 | -0.626 | no | yes | 1.26, 4.40
0.30 | -0.09 | 1.21 | -0.370 | no | yes | 1.91, 5.05
0.40 | -0.06 | 1.17 | -0.503 | no | yes | 2.51, 5.65
0.50 | -0.03 | 0.96 | -0.986 | no | no | 3.17, 0.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00
footR: 0.00
footL: 0.00
balance: 0.00

## Round 1: your reply

Round 0 fell backward within 0.5 s. The stance leg's negative thigh torque (the swing-phase half of the cosine) pitched the torso back, and the balance feedback was too weak to counter it. This revision halves the rhythmic thigh amplitude, raises the balance gains roughly threefold, adds a small forward-torque bias on both thighs, and softens the knee and foot drives.

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
 "bias": {"a0": 0.1, "a3": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"cos(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "thighL", "inputs": {"cos(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a3": 0.3}},
  {"type": "reflex", "name": "kneeR", "inputs": {"cos(R)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a1": -0.3}},
  {"type": "reflex", "name": "kneeL", "inputs": {"cos(L)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a4": -0.3}},
  {"type": "linear", "name": "footR", "inputs": {"sin(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a2": 0.1}},
  {"type": "linear", "name": "footL", "inputs": {"sin(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a5": 0.1}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.77 | 0.94 | torso angle out of range
1 | -0.81 | 1.02 | torso angle out of range
2 | -0.61 | 0.80 | torso angle out of range
3 | -0.71 | 0.89 | torso angle out of range
4 | -0.68 | 0.85 | torso angle out of range
5 | -0.66 | 0.82 | torso angle out of range
6 | -0.79 | 0.97 | torso angle out of range
7 | -0.75 | 0.90 | torso angle out of range
8 | -0.69 | 0.86 | torso angle out of range
9 | -0.79 | 0.96 | torso angle out of range

Over the 10 episodes: mean d -0.73 m, min -0.81, max -0.61; mean time survived 0.90 s; mean forward speed -0.81 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.261 | 0.043 | 0.79 | 0.41
right leg | -1.329 | 0.003 | 0.26 | 0.00
right foot | 0.004 | 0.849 | 0.07 | 0.00
left thigh | -0.110 | 0.042 | 0.83 | 0.58
left leg | -0.636 | 0.004 | 0.26 | 0.00
left foot | -0.164 | 0.882 | 0.07 | 0.00
torso angle min -0.972, max -0.005 rad; torso height min 0.90, max 1.25 m
right foot: on the ground 0.43 of the steps, 1 touchdowns
left foot: on the ground 0.71 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.03 | 1.20 | -0.160 | no | yes | 0.65, 3.80
0.20 | -0.05 | 1.19 | -0.175 | no | yes | 1.26, 4.40
0.30 | -0.08 | 1.20 | -0.168 | no | yes | 1.91, 5.05
0.40 | -0.13 | 1.19 | -0.184 | no | yes | 2.51, 5.65
0.50 | -0.20 | 1.18 | -0.244 | no | yes | 3.17, 0.03
0.60 | -0.29 | 1.18 | -0.267 | yes | no | 3.77, 0.63
0.70 | -0.41 | 1.15 | -0.374 | yes | yes | 4.42, 1.28
0.80 | -0.55 | 1.10 | -0.548 | yes | yes | 5.03, 1.88
0.90 | -0.73 | 0.96 | -0.874 | yes | no | 5.68, 2.54

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00
footR: 0.00
footL: 0.00
balance: 0.00

## Round 2: your reply

Both runs fell backward. In round 1 the thigh torques were saturated and the thighs sat against the joint limit near 0, so thigh balance torque alone could not catch the fall. This revision adds balance feedback at the ankles, where positive torque pushes the body forward, strengthens the thigh feedback, and weakens the rhythmic drives further. I have not simulated it.

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
 "bias": {"a0": 0.15, "a3": 0.15},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"cos(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a0": 0.2}},
  {"type": "linear", "name": "thighL", "inputs": {"cos(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a3": 0.2}},
  {"type": "reflex", "name": "kneeR", "inputs": {"cos(R)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a1": -0.2}},
  {"type": "reflex", "name": "kneeL", "inputs": {"cos(L)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a4": -0.2}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -6.0, "obs[10]": -0.5}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0, "a2": 0.8, "a5": 0.8}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.20 | 0.42 | height too low
1 | -0.23 | 0.50 | torso angle out of range
2 | -0.19 | 0.42 | height too low
3 | -0.21 | 0.47 | height too low
4 | -0.20 | 0.42 | height too low
5 | -0.21 | 0.45 | torso angle out of range
6 | -0.21 | 0.45 | torso angle out of range
7 | -0.21 | 0.42 | height too low
8 | -0.21 | 0.48 | torso angle out of range
9 | -0.22 | 0.47 | torso angle out of range

Over the 10 episodes: mean d -0.21 m, min -0.23, max -0.19; mean time survived 0.45 s; mean forward speed -0.47 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.005 | 0.031 | 0.97 | 0.94
right leg | -1.671 | 0.003 | 0.17 | 0.00
right foot | 0.004 | 1.134 | 0.92 | 0.81
left thigh | -0.012 | 0.036 | 0.94 | 0.88
left leg | -1.601 | 0.003 | 0.17 | 0.00
left foot | 0.000 | 1.116 | 0.92 | 0.81
torso angle min -0.992, max -0.004 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.17 of the steps, 1 touchdowns
left foot: on the ground 0.85 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.03 | 1.19 | -0.124 | yes | yes | 0.65, 3.80
0.20 | -0.08 | 1.17 | -0.308 | no | yes | 1.26, 4.40
0.30 | -0.14 | 1.06 | -0.607 | no | yes | 1.91, 5.05
0.40 | -0.20 | 0.84 | -0.959 | no | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thighR: 0.00
thighL: 0.00
balance: 0.19

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
