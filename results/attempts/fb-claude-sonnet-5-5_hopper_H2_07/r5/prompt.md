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

This is my round-0 design. It uses one 2.5 Hz oscillator for the hop rhythm, with torso-angle and angular-velocity feedback on the thigh. The gains are initial guesses that I expect to revise after the practice results.

- **Balance:** the thigh torque is `-(3*obs[1] + 0.3*obs[7])`. A forward lean gives a negative thigh torque, which pitches the torso backward.
- **Leg:** `0.3 + 0.7*sin(phase)`, so it compresses in the negative half-cycle and extends (pushes off) in the positive half.
- **Foot:** `0.3*sin(phase)`, in phase with the leg.
- **Thigh rhythm:** `0.3*cos(phase)`, a quarter-cycle ahead of the leg, to swing the leg forward in flight.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.7, "a2": 0.3}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.93 | 1.02 | height too low
1 | 0.92 | 1.03 | height too low
2 | 0.95 | 1.01 | height too low
3 | 0.95 | 1.02 | height too low
4 | 0.96 | 1.01 | height too low
5 | 0.95 | 1.02 | height too low
6 | 0.94 | 1.02 | height too low
7 | 0.95 | 1.01 | height too low
8 | 0.91 | 1.03 | height too low
9 | 0.94 | 1.02 | height too low

Over the 10 episodes: mean d 0.94 m, min 0.91, max 0.96; mean time survived 1.02 s; mean forward speed 0.92 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.336 | 0.030 | 0.31 | 0.04
leg | -0.763 | 0.112 | 0.53 | 0.05
foot | 0.004 | 0.828 | 0.19 | 0.00
torso angle min -0.107, max 0.136 rad; torso height min 0.70, max 1.25 m
foot: on the ground 0.50 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.007 | yes | 1.63
0.20 | 0.06 | 1.22 | -0.031 | yes | 3.14
0.30 | 0.14 | 1.21 | -0.079 | no | 4.78
0.40 | 0.17 | 1.19 | -0.053 | yes | 0.00
0.50 | 0.22 | 1.19 | -0.019 | no | 1.63
0.60 | 0.36 | 1.19 | -0.083 | no | 3.14
0.70 | 0.49 | 1.14 | -0.088 | no | 4.78
0.80 | 0.59 | 1.05 | -0.015 | yes | 6.28
0.90 | 0.77 | 0.98 | 0.125 | no | 1.63
1.00 | 0.92 | 0.75 | -0.050 | no | 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
sin_drive: 0.00
cos_drive: 0.00

## Round 1: your reply

Round 0 hopped forward (about 0.92 m/s) but sank until the torso fell below 0.7 m at about 1 s. For round 1 I'm making the leg stiffer, with a higher extension bias and a smaller compression swing. I'm also shrinking the thigh and foot rhythm amplitudes so they disturb the torso less, and raising the balance gains slightly.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.5},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.15}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.15}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.94 | 1.17 | height too low
1 | 0.93 | 1.18 | height too low
2 | 0.92 | 1.14 | height too low
3 | 0.93 | 1.14 | height too low
4 | 0.92 | 1.13 | height too low
5 | 0.93 | 1.15 | height too low
6 | 0.93 | 1.16 | height too low
7 | 0.91 | 1.14 | height too low
8 | 0.94 | 1.18 | height too low
9 | 0.93 | 1.16 | height too low

Over the 10 episodes: mean d 0.93 m, min 0.91, max 0.94; mean time survived 1.15 s; mean forward speed 0.80 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.209 | 0.003 | 0.03 | 0.00
leg | 0.001 | 0.003 | 0.50 | 0.00
foot | 0.004 | 0.803 | 0.10 | 0.00
torso angle min -0.024, max 0.026 rad; torso height min 0.70, max 1.25 m
foot: on the ground 0.92 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.003 | yes | 1.63
0.20 | 0.04 | 1.20 | -0.013 | yes | 3.14
0.30 | 0.09 | 1.20 | -0.022 | yes | 4.78
0.40 | 0.11 | 1.20 | 0.007 | yes | 0.00
0.50 | 0.14 | 1.20 | 0.021 | yes | 1.63
0.60 | 0.21 | 1.19 | -0.006 | yes | 3.14
0.70 | 0.31 | 1.16 | -0.019 | yes | 4.78
0.80 | 0.39 | 1.13 | 0.010 | yes | 6.28
0.90 | 0.50 | 1.07 | 0.025 | yes | 1.63
1.00 | 0.65 | 0.95 | -0.000 | yes | 3.14
1.10 | 0.84 | 0.80 | -0.012 | yes | 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
sin_drive: 0.00
cos_drive: 0.00

## Round 2: your reply

Round 1 shows the leg locked straight (leg angle about 0) while the thigh angle drifted to about -1.2 rad. The thigh had almost no torque (mean |action| 0.03), so the foot slid backward and the torso sank. For round 2 I'm adding thigh angle and velocity feedback to hold the thigh near vertical. I'm also adding a small thigh bias so the torso settles at a slight forward lean and drifts forward.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 0.5},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4, "obs[2]": 2.0, "obs[8]": 0.2},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.15}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.15}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.46 | 0.86 | torso angle out of range
1 | 0.46 | 0.88 | torso angle out of range
2 | 0.45 | 0.83 | torso angle out of range
3 | 0.45 | 0.83 | torso angle out of range
4 | 0.45 | 0.82 | torso angle out of range
5 | 0.45 | 0.84 | torso angle out of range
6 | 0.45 | 0.86 | torso angle out of range
7 | 0.45 | 0.83 | torso angle out of range
8 | 0.45 | 0.88 | torso angle out of range
9 | 0.45 | 0.86 | torso angle out of range

Over the 10 episodes: mean d 0.45 m, min 0.45, max 0.46; mean time survived 0.85 s; mean forward speed 0.53 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.254 | 0.005 | 0.04 | 0.00
leg | 0.001 | 0.003 | 0.51 | 0.00
foot | 0.004 | 0.456 | 0.09 | 0.00
torso angle min -0.005, max 0.200 rad; torso height min 1.11, max 1.25 m
foot: on the ground 0.91 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.005 | yes | 1.63
0.20 | 0.05 | 1.21 | 0.026 | yes | 3.14
0.30 | 0.10 | 1.20 | 0.046 | yes | 4.78
0.40 | 0.12 | 1.20 | 0.074 | yes | 0.00
0.50 | 0.15 | 1.20 | 0.092 | yes | 1.63
0.60 | 0.22 | 1.19 | 0.098 | yes | 3.14
0.70 | 0.32 | 1.16 | 0.126 | yes | 4.78
0.80 | 0.40 | 1.13 | 0.172 | yes | 6.28

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
sin_drive: 0.00
cos_drive: 0.00

## Round 3: your reply

Round 2 stood on a locked-straight leg and tipped forward, so it never hopped. Round 0 was the only design that hopped, though it sank and let the thigh drift back to about -1.3 rad. For round 3 I'm going back to the round-0 leg drive (0.3 bias, 0.7 swing) so the leg compresses and pushes off again. I'm keeping the thigh angle and velocity feedback from round 2 to stop that drift. The thigh bias drops from 0.2 to 0.1 to reduce the forward-tipping torque seen in round 2.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4, "obs[2]": 2.0, "obs[8]": 0.2},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.7, "a2": 0.3}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.67 | 0.86 | torso angle out of range
1 | 0.66 | 0.87 | torso angle out of range
2 | 0.68 | 0.86 | torso angle out of range
3 | 0.68 | 0.86 | torso angle out of range
4 | 0.68 | 0.85 | torso angle out of range
5 | 0.67 | 0.86 | torso angle out of range
6 | 0.67 | 0.86 | torso angle out of range
7 | 0.68 | 0.86 | torso angle out of range
8 | 0.65 | 0.87 | torso angle out of range
9 | 0.67 | 0.86 | torso angle out of range

Over the 10 episodes: mean d 0.67 m, min 0.65, max 0.68; mean time survived 0.86 s; mean forward speed 0.78 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.360 | 0.016 | 0.22 | 0.06
leg | -0.689 | 0.088 | 0.49 | 0.04
foot | 0.004 | 0.816 | 0.18 | 0.00
torso angle min -0.096, max 0.192 rad; torso height min 1.04, max 1.25 m
foot: on the ground 0.61 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.009 | yes | 1.63
0.20 | 0.07 | 1.23 | 0.019 | yes | 3.14
0.30 | 0.15 | 1.22 | 0.023 | no | 4.78
0.40 | 0.18 | 1.19 | -0.052 | yes | 0.00
0.50 | 0.22 | 1.19 | 0.001 | no | 1.63
0.60 | 0.37 | 1.20 | 0.105 | no | 3.14
0.70 | 0.50 | 1.14 | 0.146 | no | 4.78
0.80 | 0.59 | 1.06 | 0.154 | yes | 6.28

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
sin_drive: 0.00
cos_drive: 0.00

## Round 4: your reply

Round 3 hopped but pitched forward while airborne. In flight, the thigh-torque reaction on the torso has the opposite sign to the one on the ground, so my strong balance gains pushed the torso further over. For round 4 I'm lowering the balance gains and the thigh rhythm and bias, keeping the thigh angle feedback to stop the backward drift. I'm also raising the leg extension bias a little to reduce the sinking seen in round 0.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 0.4},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 2.5, "obs[7]": 0.25, "obs[2]": 1.5, "obs[8]": 0.15},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.6, "a2": 0.25}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.2}}
 ]}
```

## Round 4: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.56 | 0.77 | torso angle out of range
1 | 0.55 | 0.78 | torso angle out of range
2 | 0.56 | 0.76 | torso angle out of range
3 | 0.56 | 0.76 | torso angle out of range
4 | 0.55 | 0.74 | torso angle out of range
5 | 0.56 | 0.76 | torso angle out of range
6 | 0.56 | 0.77 | torso angle out of range
7 | 0.56 | 0.76 | torso angle out of range
8 | 0.56 | 0.78 | torso angle out of range
9 | 0.56 | 0.77 | torso angle out of range

Over the 10 episodes: mean d 0.56 m, min 0.55, max 0.56; mean time survived 0.76 s; mean forward speed 0.73 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.325 | 0.004 | 0.06 | 0.00
leg | -0.117 | 0.030 | 0.48 | 0.04
foot | 0.004 | 0.645 | 0.16 | 0.00
torso angle min -0.005, max 0.194 rad; torso height min 1.05, max 1.25 m
foot: on the ground 0.86 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.007 | yes | 1.63
0.20 | 0.06 | 1.22 | 0.016 | yes | 3.14
0.30 | 0.15 | 1.20 | 0.030 | yes | 4.78
0.40 | 0.19 | 1.21 | 0.075 | yes | 0.00
0.50 | 0.24 | 1.18 | 0.123 | yes | 1.63
0.60 | 0.34 | 1.17 | 0.131 | yes | 3.14
0.70 | 0.48 | 1.11 | 0.167 | yes | 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
balance: 0.00
sin_drive: 0.00
cos_drive: 0.00

## Now: round 5 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). This is the last round: this design is final and is the one scored. You may resubmit an earlier design unchanged by copying
its spec.
