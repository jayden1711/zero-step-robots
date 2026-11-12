# Task: design the controller network of a simulated walking robot

You will design the controller of a simulated robot. You cannot run code yourself. After each design you write, we
test it on 10 practice episodes and send you a fixed summary of the results; you then revise it. There are 6 designs in
total: this first one (round 0) and 5 revisions (rounds 1 to 5). Your round-5 design is final and is scored exactly as
written, on different episodes from the practice ones. There is no training: the numbers you write become the final
weights of the controller network.

## The robot and environment

Environment: Gymnasium `Hopper-v5` (MuJoCo), a planar one-legged robot (torso, thigh, leg, foot) that moves in
the x-z plane. Forward is +x.

- Observation `obs` (11 numbers, raw, not normalised; indices from 0):
  - obs[0]: height (z) of the torso
  - obs[1]: torso angle (radians)
  - obs[2]: thigh joint angle
  - obs[3]: leg joint angle
  - obs[4]: foot joint angle
  - obs[5]: torso x-velocity
  - obs[6]: torso z-velocity
  - obs[7]: torso angular velocity
  - obs[8]: thigh joint angular velocity
  - obs[9]: leg joint angular velocity
  - obs[10]: foot joint angular velocity

  Velocities (obs[5] to obs[10]) are clipped to [-10, 10].
- Action (3 numbers): the torques at the thigh, leg and foot joints, in that order (a0, a1, a2). Values outside
  [-1, 1] are clipped to that range.
- One step is 0.008 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.005).

Episode rules:

- The hopper is healthy while all of these hold: torso height z > 0.7; |torso angle| < 0.2 radians; and every
  joint angle and velocity is strictly inside (-100, 100).
- The episode terminates as soon as the hopper is not healthy. Otherwise it is cut off after 1000 steps.
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

A workable structure for this robot is a hopping gait driven by one rhythm:

- One oscillator sets the hop cycle. Within each cycle the leg (thigh, leg and foot joints) compresses on landing
  and then extends to push off (stance); in the air the thigh swings the leg forward ready for the next landing
  (flight). The phase relationship between the joints is fixed by how each joint's command is taken from the
  oscillator's cos and sin outputs.
- Balance feedback is added on top of the rhythm: the torso angle (obs[1]) and the torso angular velocity (obs[7])
  feed back to the thigh joint so the torso stays upright, and forward speed is regulated through how far the
  torso leans.

Facts and ranges (from the model files and the documentation, not tuned for you):

- Sign conventions. A positive torso angle (obs[1]) means the torso leans forward (towards +x). For the thigh, leg
  and foot joints, a positive torque drives the joint angle up, and a negative joint angle swings the part below the
  joint backwards (towards -x). The thigh and leg joint angles are limited to [-2.62, 0] radians (0 = straight
  in line with the part above), the foot to [-0.79, 0.79].
- With the foot on the ground, a negative thigh torque pitches the torso backward (the reaction at the hip).
- Admissible ranges: oscillator frequency 1 to 4 Hz for a hop cycle of a robot this size; rhythmic torque
  amplitude up to 1 (the action limit) per joint; feedback that holds the torso upright opposes the sign of
  obs[1] and of obs[7] at the thigh joint.

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
10), `cos(NAME)` or `sin(NAME)` for an oscillator called NAME. Actions are named `a0` to a2.

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

    {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
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

This is a first guess, since I can't simulate it. The design uses one 2 Hz oscillator, a PD balance reflex on the thigh with a small forward-lean bias, and the leg and foot driven by the oscillator's sin output.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15, "a1": 0.3, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.2, "a1": 0.7, "a2": 0.3}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.97 | 0.91 | height too low
1 | 0.97 | 0.92 | height too low
2 | 0.95 | 0.89 | height too low
3 | 0.96 | 0.90 | height too low
4 | 0.94 | 0.88 | height too low
5 | 0.95 | 0.90 | height too low
6 | 0.97 | 0.91 | height too low
7 | 0.95 | 0.90 | height too low
8 | 0.97 | 0.93 | height too low
9 | 0.97 | 0.91 | height too low

Over the 10 episodes: mean d 0.96 m, min 0.94, max 0.97; mean time survived 0.90 s; mean forward speed 1.06 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.335 | 0.032 | 0.32 | 0.07
leg | -0.980 | 0.108 | 0.51 | 0.04
foot | 0.004 | 0.809 | 0.19 | 0.00
torso angle min -0.129, max 0.135 rad; torso height min 0.71, max 1.25 m
foot: on the ground 0.53 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.008 | yes | 1.31
0.20 | 0.07 | 1.22 | 0.050 | yes | 2.51
0.30 | 0.17 | 1.23 | -0.008 | yes | 3.82
0.40 | 0.25 | 1.18 | -0.067 | no | 5.03
0.50 | 0.29 | 1.15 | -0.070 | yes | 0.05
0.60 | 0.36 | 1.12 | -0.061 | no | 1.26
0.70 | 0.60 | 1.07 | 0.086 | no | 2.56
0.80 | 0.80 | 0.96 | -0.018 | no | 3.77
0.90 | 0.97 | 0.71 | -0.058 | no | 5.08

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
hop_sin: 0.00
hop_cos: 0.00

## Round 1: your reply

Round 0 failed because the leg collapsed: the torso height sank from 1.25 m to 0.71 m, while the torso angle stayed within limits. For round 1 I'm making the leg stiffer. That means a higher constant leg-extension bias, a smaller oscillator swing, and a damping term that extends the leg when the torso is moving down.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.6, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1, "a1": 0.4, "a2": 0.2}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.2}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.93 | 1.00 | height too low
1 | 0.94 | 1.02 | height too low
2 | 0.91 | 0.98 | height too low
3 | 0.92 | 0.99 | height too low
4 | 0.91 | 0.98 | height too low
5 | 0.92 | 0.98 | height too low
6 | 0.93 | 1.00 | height too low
7 | 0.92 | 0.98 | height too low
8 | 0.93 | 1.02 | height too low
9 | 0.93 | 1.00 | height too low

Over the 10 episodes: mean d 0.92 m, min 0.91, max 0.94; mean time survived 1.00 s; mean forward speed 0.93 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.158 | 0.005 | 0.06 | 0.00
leg | 0.001 | 0.003 | 0.68 | 0.15
foot | 0.004 | 0.806 | 0.13 | 0.00
torso angle min -0.021, max 0.090 rad; torso height min 0.71, max 1.25 m
foot: on the ground 0.86 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.20 | 0.006 | yes | 1.31
0.20 | 0.06 | 1.21 | 0.031 | yes | 2.51
0.30 | 0.14 | 1.20 | -0.007 | yes | 3.82
0.40 | 0.21 | 1.19 | -0.018 | yes | 5.03
0.50 | 0.27 | 1.18 | 0.037 | yes | 0.05
0.60 | 0.32 | 1.16 | 0.087 | yes | 1.26
0.70 | 0.45 | 1.11 | 0.068 | yes | 2.56
0.80 | 0.60 | 1.01 | 0.009 | no | 3.77
0.90 | 0.77 | 0.84 | -0.004 | yes | 5.08

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
height_damp: 0.00
hop_sin: 0.00
hop_cos: 0.00

## Round 2: your reply

Round 1 failed because the leg stayed locked straight while the thigh swung back to -1.16 rad, so the hopper folded forward with the foot planted. In this round I add joint-angle PD terms that hold the thigh and foot near 0. I also take the oscillator off the foot and shrink its thigh swing.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": 0.5, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -3.0, "obs[8]": -0.1},
   "range": 8.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -3.0, "obs[10]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.5}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.00 | 8.00 | cut off at 1000 steps
1 | 0.00 | 8.00 | cut off at 1000 steps
2 | -0.01 | 8.00 | cut off at 1000 steps
3 | -0.01 | 8.00 | cut off at 1000 steps
4 | -0.02 | 8.00 | cut off at 1000 steps
5 | -0.01 | 8.00 | cut off at 1000 steps
6 | -0.00 | 8.00 | cut off at 1000 steps
7 | -0.01 | 8.00 | cut off at 1000 steps
8 | 0.00 | 8.00 | cut off at 1000 steps
9 | -0.00 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d -0.01 m, min -0.02, max 0.00; mean time survived 8.00 s; mean forward speed -0.00 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.014 | 0.002 | 0.04 | 0.00
leg | 0.000 | 0.003 | 0.50 | 0.05
foot | -0.003 | 0.004 | 0.00 | 0.00
torso angle min -0.017, max 0.001 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.99 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | -0.001 | yes | 1.31
0.20 | -0.00 | 1.21 | -0.006 | yes | 2.51
0.30 | -0.01 | 1.21 | -0.016 | yes | 3.82
0.40 | -0.01 | 1.21 | -0.010 | yes | 5.03
0.50 | -0.01 | 1.21 | -0.008 | yes | 0.05
0.60 | -0.01 | 1.21 | -0.006 | yes | 1.26
0.70 | -0.00 | 1.21 | -0.008 | yes | 2.56
0.80 | -0.00 | 1.21 | -0.015 | yes | 3.77
0.90 | -0.00 | 1.21 | -0.007 | yes | 5.08
1.00 | -0.00 | 1.21 | -0.002 | yes | 0.00
1.10 | -0.00 | 1.21 | -0.003 | yes | 1.31
1.20 | -0.00 | 1.21 | -0.007 | yes | 2.51
1.30 | -0.00 | 1.21 | -0.016 | yes | 3.82
1.40 | -0.01 | 1.21 | -0.009 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
thigh_pd: 0.00
foot_pd: 0.00
height_damp: 0.00
hop_sin: 0.00
hop_cos: 0.00

## Round 3: your reply

Round 2 stood perfectly still: stable, but no hop and no lean. The leg sat at its straight limit (angle 0), so the positive-only leg command never crouched. This round changes three things:

- **Crouch and extend:** the leg command now swings negative as well as positive (bias 0.3, oscillator amplitude 0.6), so the leg compresses and then pushes off.
- **Forward lean:** the thigh holds a small negative angle (about -0.08 rad) via the `a0` bias, so the torso tips forward and the hops carry it in +x.
- **Rhythm:** the oscillator's cos and sin outputs now drive the leg as well as the thigh.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.25, "a1": 0.3, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -3.0, "obs[8]": -0.1},
   "range": 8.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -3.0, "obs[10]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.6}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.08 | 0.46 | torso angle out of range
1 | -0.07 | 0.46 | torso angle out of range
2 | -0.08 | 0.45 | torso angle out of range
3 | -0.08 | 0.45 | torso angle out of range
4 | -0.09 | 0.45 | torso angle out of range
5 | -0.09 | 0.46 | torso angle out of range
6 | -0.08 | 0.46 | torso angle out of range
7 | -0.09 | 0.45 | torso angle out of range
8 | -0.07 | 0.46 | torso angle out of range
9 | -0.07 | 0.46 | torso angle out of range

Over the 10 episodes: mean d -0.08 m, min -0.09, max -0.07; mean time survived 0.45 s; mean forward speed -0.17 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.053 | 0.010 | 0.12 | 0.05
leg | -0.302 | 0.003 | 0.47 | 0.00
foot | -0.001 | 0.070 | 0.04 | 0.00
torso angle min -0.196, max -0.005 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.81 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | -0.00 | 1.20 | -0.024 | yes | 1.31
0.20 | -0.01 | 1.21 | -0.043 | yes | 2.51
0.30 | -0.01 | 1.21 | -0.057 | yes | 3.82
0.40 | -0.04 | 1.21 | -0.090 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
thigh_pd: 0.00
foot_pd: 0.00
height_damp: 0.00
hop_sin: 0.00
hop_cos: 0.00

## Round 4: your reply

Round 3 fell backward because the negative thigh bias pitched the torso back. This round I flip the thigh bias to a small positive value for forward lean and strengthen the balance gains. I also drive the leg with a larger crouch-then-extend swing (about -0.9 to +0.9) so it actually hops instead of standing.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15, "a1": 0.0, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -3.0, "obs[8]": -0.1},
   "range": 8.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -3.0, "obs[10]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.1},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.9}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1}}
 ]}
```

## Round 4: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.05 | 0.37 | torso angle out of range
1 | -0.05 | 0.37 | torso angle out of range
2 | -0.06 | 0.37 | torso angle out of range
3 | -0.06 | 0.37 | torso angle out of range
4 | -0.06 | 0.37 | torso angle out of range
5 | -0.06 | 0.37 | torso angle out of range
6 | -0.05 | 0.37 | torso angle out of range
7 | -0.06 | 0.37 | torso angle out of range
8 | -0.05 | 0.37 | torso angle out of range
9 | -0.05 | 0.37 | torso angle out of range

Over the 10 episodes: mean d -0.06 m, min -0.06, max -0.05; mean time survived 0.37 s; mean forward speed -0.15 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.004 | 0.30 | 0.13
leg | -0.293 | 0.003 | 0.56 | 0.00
foot | -0.002 | 0.070 | 0.03 | 0.00
torso angle min -0.176, max 0.002 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.76 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | -0.00 | 1.20 | -0.001 | yes | 1.31
0.20 | -0.00 | 1.21 | -0.003 | yes | 2.51
0.30 | -0.01 | 1.21 | -0.026 | yes | 3.82

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
thigh_pd: 0.00
foot_pd: 0.00
height_damp: 0.00
hop_sin: 0.00
hop_cos: 0.00

## Now: round 5 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). This is the last round: this design is final and is the one scored. You may resubmit an earlier design unchanged by copying
its spec.
