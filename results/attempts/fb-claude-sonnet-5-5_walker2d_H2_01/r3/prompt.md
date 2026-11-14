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

This is the round-0 design: two antiphase oscillators drive thigh and knee torques, with torso-angle and angular-velocity feedback on both thighs. I could not run it, so the amplitudes, frequency and gains are untested first guesses.

- **Oscillators:** `R` and `L` start half a cycle apart and are coupled with a pi lag in both directions, so they settle in antiphase. I set the frequency to 1.2 Hz.
- **Thigh torque:** `-0.6*sin(phase)`. It is negative while sin > 0 (stance, thigh swings back) and positive in swing.
- **Knee torque:** `+0.5*sin(phase)`. It flexes the knee during swing and extends it in stance.
- **Balance:** `-(obs[1] + 0.1*obs[10])` goes to both thighs. A forward lean or forward pitch rate then gives a negative thigh torque, which pitches the torso back.
- **Feet:** left unpowered for now.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.6, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.6, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a0": -1.0, "a3": -1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.14 | 0.63 | height too low
1 | 0.12 | 0.63 | height too low
2 | 0.16 | 0.62 | height too low
3 | 0.15 | 0.63 | height too low
4 | 0.17 | 0.62 | height too low
5 | 0.16 | 0.62 | height too low
6 | 0.13 | 0.63 | height too low
7 | 0.16 | 0.62 | height too low
8 | 0.12 | 0.63 | height too low
9 | 0.13 | 0.63 | height too low

Over the 10 episodes: mean d 0.14 m, min 0.12, max 0.17; mean time survived 0.63 s; mean forward speed 0.23 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.903 | 0.073 | 0.35 | 0.15
right leg | -2.249 | 0.006 | 0.31 | 0.00
right foot | 0.004 | 0.478 | 0.00 | 0.00
left thigh | -2.445 | 0.032 | 0.60 | 0.35
left leg | -2.670 | 0.002 | 0.31 | 0.00
left foot | -0.852 | 0.202 | 0.00 | 0.00
torso angle min -0.855, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.66 of the steps, 2 touchdowns
left foot: on the ground 0.05 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.03 | 1.20 | -0.167 | yes | yes | 0.78, 3.93
0.20 | -0.10 | 1.17 | -0.587 | yes | no | 1.51, 4.65
0.30 | -0.11 | 1.14 | -0.855 | yes | no | 2.29, 5.43
0.40 | -0.06 | 1.17 | -0.593 | no | no | 3.02, 6.16
0.50 | 0.07 | 1.18 | -0.199 | yes | no | 3.80, 0.66
0.60 | 0.14 | 0.92 | -0.547 | no | no | 4.52, 1.38

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
right_leg_rhythm: 0.00
left_leg_rhythm: 0.00
torso_balance: 0.00

## Round 1: your reply

I changed the design in four ways to address the backward fall seen in round 0:

- **Balance:** the balance gain is stronger, since seed 0 pitched back to -0.855 rad.
- **Thigh rhythm:** the thigh rhythm amplitude is smaller.
- **Knee:** a positive knee bias keeps the legs extended in stance. In round 0 the knees collapsed to -2.2 and -2.7 rad.
- **Feet:** the feet now get a damped stiffness term.

I have not run it, so all values are still untested.

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
 "bias": {"a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.4, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.4, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15},
   "range": 2.0, "tol": 0.05, "to": {"a0": -2.0, "a3": -2.0}},
  {"type": "linear", "name": "right_ankle_hold", "inputs": {"obs[4]": 1.0, "obs[12]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a2": -1.0}},
  {"type": "linear", "name": "left_ankle_hold", "inputs": {"obs[7]": 1.0, "obs[16]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.00 | 1.57 | height too low
1 | -0.90 | 1.88 | height too low
2 | -0.98 | 1.31 | height too low
3 | -1.03 | 1.59 | height too low
4 | -1.01 | 1.64 | torso angle out of range
5 | -0.32 | 1.81 | height too low
6 | -1.02 | 1.66 | height too low
7 | -1.02 | 1.52 | height too low
8 | -0.99 | 1.42 | height too low
9 | -1.01 | 1.58 | height too low

Over the 10 episodes: mean d -0.93 m, min -1.03, max -0.32; mean time survived 1.60 s; mean forward speed -0.59 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.297 | 0.036 | 0.66 | 0.35
right leg | -1.975 | 0.010 | 0.39 | 0.00
right foot | -0.504 | 0.936 | 0.17 | 0.00
left thigh | -0.174 | 0.045 | 0.69 | 0.49
left leg | -0.597 | 0.099 | 0.28 | 0.00
left foot | -0.061 | 0.080 | 0.05 | 0.00
torso angle min -0.851, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.57 of the steps, 4 touchdowns
left foot: on the ground 0.84 of the steps, 9 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.00 | 1.20 | -0.022 | yes | yes | 0.65, 3.80
0.20 | -0.03 | 1.20 | -0.141 | yes | yes | 1.26, 4.40
0.30 | -0.08 | 1.20 | -0.292 | yes | no | 1.91, 5.05
0.40 | -0.10 | 1.20 | -0.314 | yes | yes | 2.51, 5.65
0.50 | -0.09 | 1.20 | -0.190 | yes | no | 3.17, 0.03
0.60 | -0.10 | 1.21 | -0.118 | no | no | 3.77, 0.63
0.70 | -0.15 | 1.19 | -0.206 | no | yes | 4.42, 1.28
0.80 | -0.21 | 1.19 | -0.316 | no | yes | 5.03, 1.88
0.90 | -0.27 | 1.18 | -0.269 | no | yes | 5.68, 2.54
1.00 | -0.34 | 1.16 | -0.258 | no | yes | 0.00, 3.14
1.10 | -0.51 | 1.11 | -0.390 | no | yes | 0.65, 3.80
1.20 | -0.63 | 1.04 | -0.516 | no | yes | 1.26, 4.40
1.30 | -0.75 | 1.00 | -0.571 | yes | yes | 1.91, 5.05
1.40 | -0.85 | 0.94 | -0.668 | yes | yes | 2.51, 5.65

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
right_leg_rhythm: 0.00
left_leg_rhythm: 0.00
torso_balance: 0.00
right_ankle_hold: 0.00
left_ankle_hold: 0.00

## Round 2: your reply

Round 1 pitched backward and drifted back about 1 m in every episode. Likely cause: the thigh limit at 0 wastes the positive half of the thigh rhythm, so the rhythm nets out as a backward push on the torso.

This revision makes four changes, still untested:
- **Thigh rhythm:** amplitude reduced from 0.4 to 0.25.
- **Thigh bias:** +0.25 on both thighs, to pitch the torso forward.
- **Balance:** feedback gain on torso angle and angular velocity raised.
- **Knee:** the swing flexion is kept the same.

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
 "bias": {"a0": 0.25, "a3": 0.25, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.25, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.25, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 2.0, "tol": 0.05, "to": {"a0": -3.0, "a3": -3.0}},
  {"type": "linear", "name": "right_ankle_hold", "inputs": {"obs[4]": 1.0, "obs[12]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a2": -1.0}},
  {"type": "linear", "name": "left_ankle_hold", "inputs": {"obs[7]": 1.0, "obs[16]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.80 | 1.34 | torso angle out of range
1 | -0.81 | 1.34 | torso angle out of range
2 | -0.85 | 1.14 | torso angle out of range
3 | -0.81 | 1.34 | torso angle out of range
4 | -0.83 | 1.35 | torso angle out of range
5 | -0.84 | 1.27 | torso angle out of range
6 | -0.82 | 1.35 | torso angle out of range
7 | -1.05 | 1.38 | height too low
8 | -0.80 | 1.35 | torso angle out of range
9 | -0.80 | 1.35 | torso angle out of range

Over the 10 episodes: mean d -0.84 m, min -1.05, max -0.80; mean time survived 1.32 s; mean forward speed -0.64 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.150 | 0.054 | 0.67 | 0.36
right leg | -0.236 | 0.098 | 0.39 | 0.00
right foot | -1.101 | 1.136 | 0.28 | 0.12
left thigh | -0.010 | 0.048 | 0.68 | 0.30
left leg | -0.568 | 0.023 | 0.30 | 0.00
left foot | -0.063 | 0.062 | 0.05 | 0.00
torso angle min -0.963, max 0.001 rad; torso height min 0.86, max 1.25 m
right foot: on the ground 0.73 of the steps, 5 touchdowns
left foot: on the ground 0.79 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | 0.00 | 1.20 | 0.000 | yes | yes | 0.65, 3.80
0.20 | -0.01 | 1.21 | -0.031 | yes | yes | 1.26, 4.40
0.30 | -0.03 | 1.21 | -0.083 | yes | yes | 1.91, 5.05
0.40 | -0.05 | 1.20 | -0.091 | yes | yes | 2.51, 5.65
0.50 | -0.06 | 1.21 | -0.046 | yes | yes | 3.17, 0.03
0.60 | -0.08 | 1.20 | -0.057 | yes | yes | 3.77, 0.63
0.70 | -0.10 | 1.20 | -0.088 | yes | yes | 4.42, 1.28
0.80 | -0.14 | 1.20 | -0.118 | yes | yes | 5.03, 1.88
0.90 | -0.18 | 1.20 | -0.135 | yes | no | 5.68, 2.54
1.00 | -0.24 | 1.18 | -0.185 | yes | yes | 0.00, 3.14
1.10 | -0.37 | 1.14 | -0.372 | no | yes | 0.65, 3.80
1.20 | -0.54 | 1.07 | -0.576 | yes | yes | 1.26, 4.40
1.30 | -0.73 | 0.93 | -0.856 | no | yes | 1.91, 5.05

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
right_leg_rhythm: 0.00
left_leg_rhythm: 0.00
torso_balance: 0.00
right_ankle_hold: 0.07
left_ankle_hold: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
