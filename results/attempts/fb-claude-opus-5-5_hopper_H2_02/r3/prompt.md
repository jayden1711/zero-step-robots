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

Round 0 is a conservative first design. The goal is to stay healthy for the full 1000 steps and drift forward, and to learn the phase signs from the test results.

**Structure**
- **One oscillator** at 2 Hz sets the hop rhythm.
- **Leg joint (a1)**: a PD controller holds the leg straight, and a rhythm term `0.4·cos(hop)` adds compression and push-off.
- **Foot (a2)**: a PD controller holds the foot near 0, plus a small rhythm term (`0.2·cos(hop)`).
- **Thigh (a0)**: a rhythm term `0.3·sin(hop)`, a quarter cycle out of phase with the leg, swings the leg in flight.
- **Balance on the thigh**: `−4·obs[1] − 0.5·obs[7]`, which opposes torso lean and its rate.
  - A bias of +0.15 on a0 sets a small forward-lean target (about 0.04 rad) to drive forward motion.
  - A small `−0.1·obs[5]` term reduces that lean as forward speed rises, which regulates speed.

The balance unit is linear up to |z| = 2, beyond which it saturates. That covers the action limit with margin.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.15},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.4},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.2},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.17 | 0.76 | torso angle out of range
1 | -0.17 | 0.77 | torso angle out of range
2 | -0.19 | 0.75 | torso angle out of range
3 | -0.18 | 0.76 | torso angle out of range
4 | -0.19 | 0.76 | torso angle out of range
5 | -0.18 | 0.76 | torso angle out of range
6 | -0.17 | 0.76 | torso angle out of range
7 | -0.19 | 0.75 | torso angle out of range
8 | -0.17 | 0.76 | torso angle out of range
9 | -0.17 | 0.76 | torso angle out of range

Over the 10 episodes: mean d -0.18 m, min -0.19, max -0.17; mean time survived 0.76 s; mean forward speed -0.23 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.004 | 0.61 | 0.20
leg | -0.121 | 0.011 | 0.15 | 0.00
foot | -0.104 | 0.061 | 0.09 | 0.00
torso angle min -0.195, max 0.012 rad; torso height min 1.19, max 1.25 m
foot: on the ground 0.89 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.20 | 0.004 | yes | 1.31
0.20 | 0.02 | 1.21 | 0.005 | yes | 2.51
0.30 | -0.02 | 1.21 | -0.071 | yes | 3.82
0.40 | -0.08 | 1.20 | -0.117 | yes | 5.03
0.50 | -0.12 | 1.21 | -0.099 | yes | 0.05
0.60 | -0.14 | 1.22 | -0.116 | yes | 1.26
0.70 | -0.16 | 1.20 | -0.155 | yes | 2.56

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_rhythm: 0.00
leg_pd: 0.00
leg_rhythm: 0.00
foot_pd: 0.00
foot_rhythm: 0.00

## Round 1: your reply

The round-0 controller fell backward in about 0.76 s, in every episode alike. These changes are partly a test of signs, so I've left the rhythm small for this round.

**What went wrong**

- The thigh angle stayed between -0.005 and +0.004 rad, right at its upper limit of 0.
- The thigh command was 0.61 on average and at the action limit 20% of the time. So it was pushing positive, into that limit.
- Because the joint was pinned, the hip did no work. The robot fell backward as one stiff piece, and x went negative.

**My reading of the balance sign**

The torso and all three joints rotate about the same axis. With the foot planted, a positive thigh torque increases the thigh angle, which means the torso rotates back relative to the leg. So positive torque should pitch the torso **backward**, the opposite of what the hint says. The data fits this: the positive balance command and the +0.15 bias only pressed the thigh into its stop. Round 1 tests this by reversing the balance sign. If the torso now falls forward instead, I'll reverse it back.

**Changes**

1. **Flipped balance on a0**: `+3·obs[1] + 0.3·obs[7]`. When the torso leans back, the thigh torque becomes negative, which by my reading pitches it forward.
   - The forward-lean target of about 0.05 rad now comes from a bias of -0.15.
   - Speed regulation is `+0.1·obs[5]`, so the robot leans less as it speeds up.
2. **A weak PD on the thigh toward -0.3 rad**. This keeps the hip away from its 0 limit so it can push in both directions.
3. **A slight crouch**: a PD on the leg toward -0.3 rad, so the leg joint is also off its stop.
4. **Gentler foot control**, so the foot can follow the ground.
5. **Smaller rhythm amplitudes**: 0.15 on the thigh, 0.2 on the leg and 0.1 on the foot. The goal this round is to survive and learn the signs, not to hop hard.

The bias on a0 combines the lean target (-0.15) and the thigh PD setpoint (-0.3), giving -0.45. The bias on a1 is -0.6, which is the leg PD gain of 2 times the -0.3 setpoint.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.45, "a1": -0.6},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3, "obs[5]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.0, "obs[8]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.15},
    "range": 0.3, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.2},
    "range": 0.4, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.1},
    "range": 0.2, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.01 | 0.06 | torso angle out of range
1 | -0.02 | 0.06 | torso angle out of range
2 | -0.02 | 0.06 | torso angle out of range
3 | -0.01 | 0.06 | torso angle out of range
4 | -0.01 | 0.06 | torso angle out of range
5 | -0.02 | 0.06 | torso angle out of range
6 | -0.02 | 0.06 | torso angle out of range
7 | -0.02 | 0.06 | torso angle out of range
8 | -0.02 | 0.06 | torso angle out of range
9 | -0.01 | 0.06 | torso angle out of range

Over the 10 episodes: mean d -0.01 m, min -0.02, max -0.01; mean time survived 0.06 s; mean forward speed -0.23 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.147 | -0.005 | 0.84 | 0.57
leg | -0.040 | 0.003 | 0.21 | 0.00
foot | 0.004 | 0.022 | 0.05 | 0.00
torso angle min -0.145, max -0.005 rad; torso height min 1.24, max 1.25 m
foot: on the ground 0.00 of the steps, 0 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_pd: 0.00
thigh_rhythm: 0.00
leg_pd: 0.00
leg_rhythm: 0.00
foot_pd: 0.00
foot_rhythm: 0.00

## Round 2: your reply

Round 1 was a clear sign test, and it failed fast. That tells us the sign.

**What round 1 showed**

- The robot started in the air and fell in 0.06 s, before the foot touched down.
- The thigh command was negative, and both the thigh angle (-0.147) and the torso angle (-0.145) dropped almost one-for-one.
- So a negative thigh torque drives obs[1] negative, as the hint said. My round-1 sign flip was wrong, and the balance sign from round 0 (oppose obs[1] and obs[7]) is correct.

**What actually went wrong in round 0**

- The sign was right, but the +0.15 bias held the thigh against its 0 limit.
- At that stop the hip had no range left to push the torso forward. The whole robot then tipped backward as one rigid piece.
- Hip torque alone also cannot correct a whole-body tilt while the foot is planted.

**Round 2 changes**

1. **Thigh balance in round 0's direction**: `−3·obs[1] − 0.4·obs[7]`, with a lean target of about +0.03 rad.
2. **Weak thigh PD toward −0.15 rad**, so the hip stays off its 0 stop and can push both ways.
3. **Ankle balance (new)**: `−2·obs[1] − 0.3·obs[7]` on the foot, plus a weak PD on the foot angle.
   - With the foot planted, a positive foot torque tips the body above it the same way a positive thigh torque tips the torso, i.e. toward positive obs[1].
   - This corrects the whole-body tilt that sank round 0.
4. **Leg PD toward −0.1 rad**, a slight bend, plus a moderate rhythm (0.25) so hopping can start.
5. **Thigh rhythm 0.15**, and no foot rhythm, so the ankle is used only for balance.

The biases are set as follows:

- **a0 = −0.06**: the thigh PD contributes −0.15 (gain 1 × setpoint −0.15) and the lean target contributes +0.09 (3 × 0.03).
- **a1 = −0.2**: gain 2 × setpoint −0.1.
- **a2 = +0.06**: 2 × 0.03, so the ankle aims for the same lean target as the thigh.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.06, "a1": -0.2, "a2": 0.06},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.0, "obs[8]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.15},
    "range": 0.3, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.25},
    "range": 0.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.16 | 8.00 | cut off at 1000 steps
1 | 0.16 | 8.00 | cut off at 1000 steps
2 | 0.15 | 8.00 | cut off at 1000 steps
3 | 0.15 | 8.00 | cut off at 1000 steps
4 | 0.14 | 8.00 | cut off at 1000 steps
5 | 0.15 | 8.00 | cut off at 1000 steps
6 | 0.16 | 8.00 | cut off at 1000 steps
7 | 0.15 | 8.00 | cut off at 1000 steps
8 | 0.16 | 8.00 | cut off at 1000 steps
9 | 0.16 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d 0.15 m, min 0.14, max 0.16; mean time survived 8.00 s; mean forward speed 0.02 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.214 | 0.001 | 0.02 | 0.00
leg | -0.212 | 0.006 | 0.09 | 0.00
foot | 0.004 | 0.308 | 0.07 | 0.00
torso angle min -0.043, max 0.058 rad; torso height min 1.18, max 1.25 m
foot: on the ground 0.99 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | -0.003 | yes | 1.31
0.20 | 0.02 | 1.21 | -0.028 | yes | 2.51
0.30 | 0.06 | 1.20 | -0.041 | yes | 3.82
0.40 | 0.12 | 1.20 | -0.030 | yes | 5.03
0.50 | 0.20 | 1.19 | 0.004 | yes | 0.05
0.60 | 0.25 | 1.18 | 0.041 | yes | 1.26
0.70 | 0.26 | 1.20 | 0.057 | yes | 2.56
0.80 | 0.24 | 1.20 | 0.037 | yes | 3.77
0.90 | 0.22 | 1.18 | 0.011 | yes | 5.08
1.00 | 0.23 | 1.18 | 0.017 | yes | 0.00
1.10 | 0.23 | 1.19 | 0.041 | yes | 1.31
1.20 | 0.19 | 1.19 | 0.042 | yes | 2.51
1.30 | 0.13 | 1.20 | 0.008 | yes | 3.82
1.40 | 0.11 | 1.20 | -0.019 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_pd: 0.00
thigh_rhythm: 0.00
leg_pd: 0.00
leg_rhythm: 0.00
ankle_balance: 0.00
foot_pd: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
