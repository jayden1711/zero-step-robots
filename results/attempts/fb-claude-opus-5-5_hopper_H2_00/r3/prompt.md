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

Round 0 is a conservative baseline. It balances the torso through the hip, holds the leg and foot with simple joint stiffness, and adds a moderate 2 Hz hop rhythm. The point is to learn whether the robot stays upright before pushing for speed.

- **Torso balance (to a0):** a0 = −4·obs[1] − 0.5·obs[7] − 0.15·obs[5] + 0.15. The bias sets a small forward lean (about 0.04 rad). The speed term reduces that lean as forward speed rises, which regulates speed.
- **Leg and foot stiffness:** a joint-angle and joint-velocity controller holds each joint near straight (0 rad), so the leg acts like a spring.
- **Rhythm:** one 2 Hz oscillator drives the leg joint (sin, amplitude 0.5), the foot (sin, 0.2) and the thigh (cos, 0.3). The thigh swing therefore runs a quarter cycle ahead of the leg push.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(cpg)": 0.5},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(cpg)": 0.2},
    "range": 0.3, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.15 | 0.90 | torso angle out of range
1 | -0.14 | 0.91 | torso angle out of range
2 | -0.17 | 0.89 | torso angle out of range
3 | -0.17 | 0.89 | torso angle out of range
4 | -0.18 | 0.88 | torso angle out of range
5 | -0.16 | 0.90 | torso angle out of range
6 | -0.15 | 0.90 | torso angle out of range
7 | -0.17 | 0.89 | torso angle out of range
8 | -0.14 | 0.91 | torso angle out of range
9 | -0.15 | 0.91 | torso angle out of range

Over the 10 episodes: mean d -0.16 m, min -0.18, max -0.14; mean time survived 0.90 s; mean forward speed -0.18 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.081 | 0.013 | 0.46 | 0.17
leg | -0.155 | 0.013 | 0.19 | 0.00
foot | -0.065 | 0.049 | 0.09 | 0.00
torso angle min -0.194, max 0.009 rad; torso height min 1.19, max 1.25 m
foot: on the ground 0.90 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.002 | yes | 1.31
0.20 | 0.03 | 1.21 | 0.003 | yes | 2.51
0.30 | 0.05 | 1.21 | -0.026 | yes | 3.82
0.40 | 0.03 | 1.22 | -0.017 | yes | 5.03
0.50 | -0.03 | 1.21 | -0.093 | yes | 0.05
0.60 | -0.08 | 1.20 | -0.066 | yes | 1.26
0.70 | -0.11 | 1.22 | -0.091 | yes | 2.56
0.80 | -0.13 | 1.21 | -0.115 | yes | 3.77

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_rhythm: 0.00
leg_pd: 0.00
leg_rhythm: 0.00
foot_pd: 0.00
foot_rhythm: 0.00

## Round 1: your reply

The round-0 failure was not a weak controller. The torso feedback had the wrong sign, so it made the lean worse instead of correcting it.

**Evidence:**
- Every episode followed the same path. The torso angle drifted steadily negative (−0.03, −0.09, then −0.19 rad) until it left the healthy range, and the thigh torque saturated (17% of steps).
- The +0.15 bias on a0 should have produced a slight positive torso angle. Instead the angle went negative right away.
- That means positive thigh torque *decreases* the torso angle. This fits the stated fact that negative thigh torque pitches the torso backward, but only if the backward direction is +obs[1].
- It also fits the model file. The `rooty` axis is (0, −1, 0), so a positive torso angle tips the top of the torso towards −x. The brief's "positive = forward lean" therefore appears reversed.
- With that reversal, a0 = −4·obs[1] − 0.5·obs[7] is positive feedback. Any small lean grows until the episode ends, which is exactly what we saw.

**Round 1 changes:**
- **Balance sign flipped:** a0 = +4·obs[1] + 0.6·obs[7]. If the torso pitches negative, the thigh torque goes negative, and that drives the torso angle back up.
- **Forward lean and speed regulation (new convention, forward lean = negative obs[1]):**
  - The target lean is about −0.05 rad. That needs a bias of −4·(−0.05) = +0.2 on a0.
  - A −0.1·obs[5] term shrinks the lean as speed rises.
- **Foot ankle strategy:**
  - With this convention, a positive foot angle means toe up, so a positive foot torque resists falling backward.
  - I added a small −0.25·obs[5] term to the foot.
- **Rhythm:** slightly stronger than round 0 (leg 0.6, foot 0.3, thigh swing 0.25) at the same 2 Hz. If the torso now holds, we also learn whether the robot actually hops.

This round mainly tests whether the sign diagnosis is right. If the torso then drifts positive instead, the original convention was correct and something else caused the fall.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.6, "obs[5]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": 0.25},
    "range": 0.4, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(cpg)": 0.6},
    "range": 0.7, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_balance", "inputs": {"obs[5]": -0.25},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(cpg)": 0.3},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.04 | 0.39 | torso angle out of range
1 | 0.04 | 0.39 | torso angle out of range
2 | 0.03 | 0.39 | torso angle out of range
3 | 0.03 | 0.39 | torso angle out of range
4 | 0.03 | 0.39 | torso angle out of range
5 | 0.03 | 0.39 | torso angle out of range
6 | 0.03 | 0.39 | torso angle out of range
7 | 0.03 | 0.39 | torso angle out of range
8 | 0.04 | 0.39 | torso angle out of range
9 | 0.04 | 0.39 | torso angle out of range

Over the 10 episodes: mean d 0.03 m, min 0.03, max 0.04; mean time survived 0.39 s; mean forward speed 0.08 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.180 | 0.007 | 0.40 | 0.10
leg | -0.099 | 0.003 | 0.30 | 0.00
foot | 0.004 | 0.046 | 0.12 | 0.00
torso angle min -0.170, max 0.055 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.78 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.004 | yes | 1.31
0.20 | 0.04 | 1.21 | 0.033 | yes | 2.51
0.30 | 0.07 | 1.21 | 0.053 | yes | 3.82

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.04
thigh_rhythm: 0.00
leg_pd: 0.00
leg_rhythm: 0.00
foot_pd: 0.00
foot_balance: 0.00
foot_rhythm: 0.00

## Round 2: your reply

# Round 2: lower the balance gains

## What round 1 showed

- **The sign fix was correct.** Round 0 drifted slowly and monotonically negative, which is the signature of positive feedback. Round 1 behaved differently: the torso tipped positive (+0.055), then swung to −0.2 within about 0.1 s. That is a fast, growing oscillation, not a drift. So positive thigh torque does lower obs[1], and the brief's "positive = forward lean" is reversed, as the model file's `rooty` axis (0, −1, 0) indicates.
- **The gains were far too high.** Hopper's actuators have a gear ratio of 200, so an action of 1 means about 200 N·m.
  - Kp = 4 gives about 800 N·m/rad.
  - Kd = 0.6 gives about 120 N·m·s/rad.
  - The torque is held for 0.008 s per step. At that gain the damping term overshoots within one step: it reverses the angular velocity and makes it larger, so the loop goes unstable.
  - The thigh saturating on 10% of steps and the balance unit saturating on 4% fit this.

## Round 2 changes

- **Balance gains cut sharply:** a0 = 1.2·obs[1] + 0.12·obs[7] − 0.05·obs[5] + 0.06.
  - The bias sets a target lean of −0.05 rad, which is forward in the corrected convention.
  - The speed term lowers a0 as speed rises, which reduces the forward lean.
- **Rhythm reduced:** thigh 0.15, leg 0.4, foot 0.15, at the same 2 Hz. The external periodic hip torque was probably helping drive the torso oscillation, so this round prioritises staying upright.
- **Foot speed damping halved** to −0.12·obs[5]. Positive foot torque raises the toe and pitches the body forward.
- **Leg PD unchanged.** It kept the leg near straight, which is fine for now.

If this survives, round 3 will increase the rhythm and lean for speed. If the torso still oscillates fast, I'll cut the gains further. If it drifts slowly, I'll raise Kp.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.06},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.2, "obs[7]": 0.12, "obs[5]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": 0.15},
    "range": 0.25, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(cpg)": 0.4},
    "range": 0.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_balance", "inputs": {"obs[5]": -0.12},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(cpg)": 0.15},
    "range": 0.25, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.02 | 0.34 | torso angle out of range
1 | 0.02 | 0.34 | torso angle out of range
2 | 0.01 | 0.35 | torso angle out of range
3 | 0.02 | 0.34 | torso angle out of range
4 | 0.01 | 0.35 | torso angle out of range
5 | 0.02 | 0.34 | torso angle out of range
6 | 0.02 | 0.34 | torso angle out of range
7 | 0.01 | 0.35 | torso angle out of range
8 | 0.02 | 0.34 | torso angle out of range
9 | 0.02 | 0.34 | torso angle out of range

Over the 10 episodes: mean d 0.02 m, min 0.01, max 0.02; mean time survived 0.34 s; mean forward speed 0.05 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.235 | 0.005 | 0.19 | 0.00
leg | -0.017 | 0.003 | 0.22 | 0.00
foot | 0.004 | 0.040 | 0.07 | 0.00
torso angle min -0.188, max 0.017 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.74 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.001 | yes | 1.31
0.20 | 0.02 | 1.21 | 0.015 | yes | 2.51
0.30 | 0.03 | 1.21 | -0.062 | yes | 3.82

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_rhythm: 0.00
leg_pd: 0.00
leg_rhythm: 0.00
foot_pd: 0.00
foot_balance: 0.00
foot_rhythm: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
