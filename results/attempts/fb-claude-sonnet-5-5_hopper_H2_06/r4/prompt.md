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

This is the round-0 design: a single 2 Hz oscillator drives the leg rhythm, and a torso-balance feedback unit acts on the thigh. The sign choices are untested guesses that the practice results should correct.

- **Leg and foot:** extend together in the first half of each cycle (push-off) and flex in the second half (flight).
- **Thigh:** gets a small rhythmic swing in antiphase with the leg, so it swings forward during flight.
- **Balance:** the thigh torque opposes the torso angle (obs[1]) and angular velocity (obs[7]).

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": -0.3, "a1": 0.8, "a2": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 2.0, "tol": 0.02, "to": {"a0": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.05 | 0.27 | torso angle out of range
1 | 0.05 | 0.26 | torso angle out of range
2 | 0.05 | 0.27 | torso angle out of range
3 | 0.05 | 0.27 | torso angle out of range
4 | 0.05 | 0.27 | torso angle out of range
5 | 0.05 | 0.27 | torso angle out of range
6 | 0.05 | 0.27 | torso angle out of range
7 | 0.04 | 0.27 | torso angle out of range
8 | 0.05 | 0.26 | torso angle out of range
9 | 0.05 | 0.27 | torso angle out of range

Over the 10 episodes: mean d 0.05 m, min 0.04, max 0.05; mean time survived 0.27 s; mean forward speed 0.17 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.091 | 0.024 | 0.28 | 0.15
leg | -0.579 | 0.003 | 0.53 | 0.00
foot | 0.004 | 0.282 | 0.20 | 0.00
torso angle min -0.191, max -0.005 rad; torso height min 1.19, max 1.25 m
foot: on the ground 0.59 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.22 | -0.049 | yes | 1.31
0.20 | 0.06 | 1.23 | -0.028 | yes | 2.51

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rhythm: 0.00
balance: 0.06

## Round 1: your reply

The round-0 hopper fell backward within 0.27 s, before the first push-off finished. The thigh rhythm (-0.3 at phase 0) was pitching the torso back, and the balance gain was too weak to counter it. This revision flips the thigh rhythm to a small forward drive, removes most of the leg extension while the leg is already straight, and strengthens the balance feedback.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.5, "a2": 0.2}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.03 | 0.29 | torso angle out of range
1 | 0.02 | 0.29 | torso angle out of range
2 | 0.02 | 0.30 | torso angle out of range
3 | 0.02 | 0.30 | torso angle out of range
4 | 0.02 | 0.30 | torso angle out of range
5 | 0.03 | 0.29 | torso angle out of range
6 | 0.02 | 0.29 | torso angle out of range
7 | 0.02 | 0.29 | torso angle out of range
8 | 0.02 | 0.29 | torso angle out of range
9 | 0.03 | 0.29 | torso angle out of range

Over the 10 episodes: mean d 0.02 m, min 0.02, max 0.03; mean time survived 0.29 s; mean forward speed 0.08 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.034 | 0.013 | 0.25 | 0.17
leg | -0.439 | 0.003 | 0.34 | 0.00
foot | 0.004 | 0.146 | 0.14 | 0.00
torso angle min -0.174, max 0.006 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.75 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.006 | yes | 1.31
0.20 | 0.05 | 1.21 | -0.013 | yes | 2.51

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rhythm: 0.00
balance: 0.00

## Round 2: your reply

The round-1 hopper still fell backward within 0.3 s, and the thigh was pinned at its 0 rad limit, so thigh torque alone could not hold it up. My reading is that foot torque is the stronger balance lever: a negative foot torque pitches the torso forward, and my earlier positive foot rhythm pushed it backward. This revision adds foot feedback to the balance unit with a negative gain on the same signal, and removes the foot rhythm. It also weakens the leg rhythm so the leg does not collapse. This is a guess from the sign conventions, not something I could test.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0, "a2": -0.6}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.08 | 0.30 | torso angle out of range
1 | -0.11 | 0.30 | torso angle out of range
2 | -0.06 | 0.31 | torso angle out of range
3 | -0.07 | 0.31 | torso angle out of range
4 | -0.05 | 0.31 | torso angle out of range
5 | -0.06 | 0.31 | torso angle out of range
6 | -0.09 | 0.30 | torso angle out of range
7 | -0.05 | 0.31 | torso angle out of range
8 | -0.11 | 0.29 | torso angle out of range
9 | -0.10 | 0.30 | torso angle out of range

Over the 10 episodes: mean d -0.08 m, min -0.11, max -0.05; mean time survived 0.30 s; mean forward speed -0.26 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.003 | 0.32 | 0.18
leg | -0.228 | 0.003 | 0.21 | 0.00
foot | -0.179 | 0.015 | 0.26 | 0.11
torso angle min -0.185, max 0.000 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.71 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | -0.000 | yes | 1.31
0.20 | -0.00 | 1.21 | -0.015 | yes | 2.51

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rhythm: 0.00
balance: 0.00

## Round 3: your reply

Round 3 is a guess from the round 0 to 2 results, since all three fell backward in about 0.3 s. Two changes:

- **Foot feedback:** the negative gain in round 2 made the backward drift worse (d went from about +0.02 to -0.08), so I'm flipping it to positive.
- **Knee bend:** I added a constant negative leg bias so the knee flexes. Earlier runs show the thigh pinned at its 0 rad limit, where balance torque on it does nothing, and a bent knee should get it off that limit.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": -0.3},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0, "a2": 0.6}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.02 | 0.20 | torso angle out of range
1 | -0.01 | 0.20 | torso angle out of range
2 | -0.03 | 0.21 | torso angle out of range
3 | -0.02 | 0.21 | torso angle out of range
4 | -0.03 | 0.21 | torso angle out of range
5 | -0.02 | 0.21 | torso angle out of range
6 | -0.02 | 0.20 | torso angle out of range
7 | -0.03 | 0.21 | torso angle out of range
8 | -0.01 | 0.20 | torso angle out of range
9 | -0.01 | 0.20 | torso angle out of range

Over the 10 episodes: mean d -0.02 m, min -0.03, max -0.01; mean time survived 0.20 s; mean forward speed -0.09 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.003 | 0.48 | 0.28
leg | -0.393 | 0.003 | 0.22 | 0.00
foot | -0.003 | 0.355 | 0.36 | 0.16
torso angle min -0.175, max -0.000 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.56 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | -0.00 | 1.20 | -0.017 | yes | 1.31

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
rhythm: 0.00
balance: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
