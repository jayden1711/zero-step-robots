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

This is my first-round design: two 1 Hz oscillators held in antiphase, each driving one leg, plus torso-angle feedback on both thighs. I couldn't simulate it, so the gains and the sign of the balance term are reasoned guesses, not tested values.

- **Rhythm:** the thigh torque follows `sin(phase)`, positive in swing and negative in stance. The knee torque is the opposite sign, so the knee flexes during swing. The foot gets a small torque in phase with the thigh.
- **Balance:** a forward lean (positive `obs[1]`) produces a negative thigh torque, which pitches the torso back. `obs[10]` adds damping.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rightLeg", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.6, "a1": -0.5, "a2": 0.2}},
  {"type": "linear", "name": "leftLeg", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.6, "a4": -0.5, "a5": 0.2}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1}, "range": 3.0, "tol": 0.05,
   "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.07 | 0.10 | torso angle out of range
1 | -0.06 | 0.10 | torso angle out of range
2 | -0.07 | 0.10 | torso angle out of range
3 | -0.07 | 0.10 | torso angle out of range
4 | -0.07 | 0.10 | torso angle out of range
5 | -0.07 | 0.10 | torso angle out of range
6 | -0.07 | 0.10 | torso angle out of range
7 | -0.07 | 0.10 | torso angle out of range
8 | -0.06 | 0.10 | torso angle out of range
9 | -0.06 | 0.10 | torso angle out of range

Over the 10 episodes: mean d -0.07 m, min -0.07, max -0.06; mean time survived 0.10 s; mean forward speed -0.68 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.946 | 0.003 | 0.38 | 0.23
right leg | -0.130 | 0.003 | 0.15 | 0.00
right foot | 0.004 | 0.266 | 0.06 | 0.00
left thigh | -0.970 | 0.001 | 0.51 | 0.38
left leg | 0.002 | 0.013 | 0.15 | 0.00
left foot | -0.074 | 0.085 | 0.06 | 0.00
torso angle min -0.860, max -0.005 rad; torso height min 1.14, max 1.25 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.23 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rightLeg: 0.00
leftLeg: 0.00
balance: 0.00

## Round 1: your reply

Round 0 fell backward within 0.1 s. The balance gain on the thighs had the wrong sign: a backward lean (negative `obs[1]`) produced a negative thigh torque, which pitches the torso back further. This revision flips the balance gains to negative and lowers the rhythm amplitude.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rightLeg", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.4, "a1": -0.4, "a2": 0.15}},
  {"type": "linear", "name": "leftLeg", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.4, "a4": -0.4, "a5": 0.15}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.13}, "range": 3.0, "tol": 0.05,
   "to": {"a0": -1.5, "a3": -1.5}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.10 | 0.90 | height too low
1 | -0.10 | 0.91 | height too low
2 | -0.05 | 0.86 | height too low
3 | -0.07 | 0.87 | height too low
4 | -0.05 | 0.91 | height too low
5 | -0.05 | 0.90 | height too low
6 | -0.10 | 0.90 | height too low
7 | -0.04 | 0.90 | height too low
8 | -0.08 | 0.89 | height too low
9 | -0.11 | 0.90 | height too low

Over the 10 episodes: mean d -0.08 m, min -0.11, max -0.04; mean time survived 0.89 s; mean forward speed -0.08 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.515 | 0.035 | 0.51 | 0.18
right leg | -2.677 | 0.089 | 0.26 | 0.00
right foot | -1.044 | 0.848 | 0.10 | 0.00
left thigh | -0.416 | 0.037 | 0.44 | 0.20
left leg | -2.384 | 0.006 | 0.26 | 0.00
left foot | -0.137 | 0.892 | 0.10 | 0.00
torso angle min -0.495, max -0.005 rad; torso height min 0.80, max 1.25 m
right foot: on the ground 0.09 of the steps, 2 touchdowns
left foot: on the ground 0.65 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.02 | 1.20 | -0.095 | yes | yes | 0.65, 3.80
0.20 | -0.06 | 1.20 | -0.297 | no | yes | 1.26, 4.40
0.30 | -0.09 | 1.19 | -0.423 | no | yes | 1.91, 5.05
0.40 | -0.11 | 1.19 | -0.331 | no | yes | 2.51, 5.65
0.50 | -0.15 | 1.20 | -0.163 | no | yes | 3.17, 0.03
0.60 | -0.17 | 1.19 | -0.184 | no | yes | 3.77, 0.63
0.70 | -0.22 | 1.15 | -0.398 | no | no | 4.42, 1.28
0.80 | -0.20 | 1.04 | -0.493 | no | no | 5.03, 1.88

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rightLeg: 0.00
leftLeg: 0.00
balance: 0.00

## Round 2: your reply

Round 1 survived 0.9 s but the knees collapsed (knee angle reached -2.68, near the limit) and the torso pitched back. This revision keeps the knees braced with a positive bias, flexing them only during swing through a reflex. It also drops the foot rhythm, lowers the thigh amplitude, and adds a small forward-lean target to the balance term. The gains are still guesses.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "rightThigh", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.3}},
  {"type": "linear", "name": "leftThigh", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.3}},
  {"type": "reflex", "name": "rightKnee", "inputs": {"sin(R)": 1.0}, "threshold": 0.2,
   "sharpness": 5.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "leftKnee", "inputs": {"sin(L)": 1.0}, "threshold": 0.2,
   "sharpness": 5.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.13}, "range": 3.0, "tol": 0.05,
   "to": {"a0": -1.5, "a3": -1.5}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.33 | 1.05 | height too low
1 | 0.42 | 1.35 | height too low
2 | 0.33 | 1.02 | height too low
3 | 0.31 | 1.02 | height too low
4 | 0.33 | 1.02 | height too low
5 | 0.33 | 1.03 | height too low
6 | 0.31 | 1.06 | height too low
7 | 0.33 | 1.03 | height too low
8 | 0.37 | 1.30 | height too low
9 | 0.55 | 1.19 | height too low

Over the 10 episodes: mean d 0.36 m, min 0.31, max 0.55; mean time survived 1.11 s; mean forward speed 0.33 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -1.048 | 0.036 | 0.47 | 0.13
right leg | -1.379 | 0.294 | 0.48 | 0.00
right foot | -0.831 | 0.952 | 0.00 | 0.00
left thigh | -0.338 | 0.068 | 0.42 | 0.19
left leg | -1.740 | 0.013 | 0.49 | 0.00
left foot | -0.713 | 0.730 | 0.00 | 0.00
torso angle min -0.384, max 0.002 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.29 of the steps, 3 touchdowns
left foot: on the ground 0.53 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.01 | 1.20 | -0.034 | yes | yes | 0.65, 3.80
0.20 | -0.04 | 1.20 | -0.221 | no | yes | 1.26, 4.40
0.30 | -0.06 | 1.19 | -0.327 | no | yes | 1.91, 5.05
0.40 | -0.04 | 1.20 | -0.299 | no | yes | 2.51, 5.65
0.50 | -0.01 | 1.20 | -0.146 | no | yes | 3.17, 0.03
0.60 | 0.07 | 1.19 | -0.010 | no | yes | 3.77, 0.63
0.70 | -0.03 | 1.15 | -0.298 | no | no | 4.42, 1.28
0.80 | -0.08 | 1.05 | -0.382 | no | no | 5.03, 1.88
0.90 | 0.05 | 0.99 | -0.206 | yes | no | 5.68, 2.54
1.00 | 0.23 | 0.87 | -0.063 | yes | no | 0.00, 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rightThigh: 0.00
leftThigh: 0.00
balance: 0.00

## Round 3: your reply

Round 2 still fell backward within about a second, with the torso angle going negative and the feet flopping. This revision makes four changes:

- **Balance:** the torso-angle gain is stronger (-3 on the thighs) and the angular-velocity damping is stronger.
- **Ankles:** a PD term on each foot keeps it flat.
- **Knees:** the stance bias is slightly higher.
- **Thigh rhythm:** the amplitude is slightly lower.

The gains are still untested guesses.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.2, "a3": 0.2, "a1": 0.25, "a4": 0.25},
 "units": [
  {"type": "linear", "name": "rightThigh", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.25}},
  {"type": "linear", "name": "leftThigh", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.25}},
  {"type": "reflex", "name": "rightKnee", "inputs": {"sin(R)": 1.0}, "threshold": 0.2,
   "sharpness": 5.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "leftKnee", "inputs": {"sin(L)": 1.0}, "threshold": 0.2,
   "sharpness": 5.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2}, "range": 3.0, "tol": 0.05,
   "to": {"a0": -3.0, "a3": -3.0}},
  {"type": "linear", "name": "rightFoot", "inputs": {"obs[4]": 1.0, "obs[15]": 0.05}, "range": 3.0, "tol": 0.05,
   "to": {"a2": -1.0}},
  {"type": "linear", "name": "leftFoot", "inputs": {"obs[7]": 1.0, "obs[16]": 0.05}, "range": 3.0, "tol": 0.05,
   "to": {"a5": -1.0}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.86 | 1.43 | torso angle out of range
1 | -0.95 | 1.50 | torso angle out of range
2 | -1.00 | 1.46 | height too low
3 | -0.91 | 1.42 | torso angle out of range
4 | -1.01 | 1.46 | height too low
5 | -0.99 | 1.48 | height too low
6 | -0.87 | 1.44 | torso angle out of range
7 | -0.93 | 1.42 | height too low
8 | -0.93 | 1.50 | height too low
9 | -0.86 | 1.42 | torso angle out of range

Over the 10 episodes: mean d -0.93 m, min -1.01, max -0.86; mean time survived 1.46 s; mean forward speed -0.64 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.261 | 0.045 | 0.80 | 0.45
right leg | -0.651 | 0.092 | 0.42 | 0.00
right foot | -0.621 | 0.675 | 0.19 | 0.00
left thigh | -0.083 | 0.061 | 0.73 | 0.47
left leg | -0.499 | 0.051 | 0.57 | 0.00
left foot | -0.117 | 0.094 | 0.04 | 0.00
torso angle min -0.984, max 0.002 rad; torso height min 0.86, max 1.25 m
right foot: on the ground 0.72 of the steps, 7 touchdowns
left foot: on the ground 0.67 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.010 | yes | yes | 0.65, 3.80
0.20 | -0.02 | 1.21 | -0.062 | yes | yes | 1.26, 4.40
0.30 | -0.03 | 1.21 | -0.098 | yes | yes | 1.91, 5.05
0.40 | -0.05 | 1.20 | -0.112 | yes | yes | 2.51, 5.65
0.50 | -0.06 | 1.21 | -0.087 | yes | yes | 3.17, 0.03
0.60 | -0.09 | 1.21 | -0.116 | yes | yes | 3.77, 0.63
0.70 | -0.15 | 1.20 | -0.303 | yes | no | 4.42, 1.28
0.80 | -0.18 | 1.19 | -0.246 | yes | yes | 5.03, 1.88
0.90 | -0.24 | 1.19 | -0.220 | yes | yes | 5.68, 2.54
1.00 | -0.32 | 1.17 | -0.295 | no | yes | 0.00, 3.14
1.10 | -0.38 | 1.17 | -0.282 | no | yes | 0.65, 3.80
1.20 | -0.47 | 1.15 | -0.321 | no | no | 1.26, 4.40
1.30 | -0.64 | 1.06 | -0.573 | yes | no | 1.91, 5.05
1.40 | -0.82 | 0.92 | -0.879 | no | no | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rightThigh: 0.00
leftThigh: 0.00
balance: 0.00
rightFoot: 0.00
leftFoot: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
