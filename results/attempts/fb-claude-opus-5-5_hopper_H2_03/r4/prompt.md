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

Round 0 is a conservative baseline: a mild knee-driven hop on a stiff, balanced posture. Since I can't run anything, the main aim is to learn whether the balance loops keep the robot upright, and only then push for speed.

**Rhythm.** One 2 Hz oscillator `P` drives the knee's target angle: `q3_ref = -0.25 - 0.25·cos(P)`.
- It starts at `phase0 = π`, where the target is a straight leg, matching the initial pose.
- The knee then compresses to -0.5 rad and extends again once per cycle.
- The knee uses PD tracking: `a1 = 2·(q3_ref − q3) − 0.1·q̇3`.

**Torso balance (hip, a0).** `a0 = −2.0·θ − 0.15·θ̇`.
- This should give a natural frequency of about 18 rad/s and damping ratio ≈ 0.7, using effective inertia ≈ joint armature 1 + torso.
- A weak spring holds the thigh near −0.1 rad, so in flight the leg returns toward vertical.

**Whole-body balance and speed (ankle, a2).**
- Because thigh and leg angles are both ≤ 0, crouching forces the shin to lean forward. The ankle therefore regulates the thigh's absolute angle `α_t = q2 − θ` toward a slightly forward-leaning reference, rather than regulating the centre of mass directly.
- Gains are stiffness 1.5 and damping 0.26 on `q̇2 − θ̇`. The robot leans further forward when it is below a target speed of 0.5 m/s (gain 0.15).
- A second term `0.5·(θ − q2 − q3 − q4)` keeps the foot level with the ground in flight. In stance, with the foot flat, this term is zero.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.15},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.3, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

What I'll read from the results:
- **Very short episodes (< 100 steps):** probably a sign error or an unstable gain in the torso or ankle loop.
- **Long episodes with little displacement:** balance works, so the next step is a stronger push-off (larger knee amplitude, ankle push in phase, higher speed target).
- **Falls after some forward travel:** speed regulation needs tightening.

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 6.49 | 8.00 | cut off at 1000 steps
1 | 6.31 | 8.00 | cut off at 1000 steps
2 | 5.67 | 8.00 | cut off at 1000 steps
3 | 5.97 | 8.00 | cut off at 1000 steps
4 | 6.01 | 8.00 | cut off at 1000 steps
5 | 5.71 | 8.00 | cut off at 1000 steps
6 | 6.87 | 7.34 | height too low
7 | 5.57 | 8.00 | cut off at 1000 steps
8 | 5.94 | 6.69 | height too low
9 | 6.81 | 7.38 | torso angle out of range

Over the 10 episodes: mean d 6.14 m, min 5.57, max 6.87; mean time survived 7.74 s; mean forward speed 0.80 m/s; episodes with d >= 3 m: 10

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.653 | 0.008 | 0.09 | 0.00
leg | -0.591 | 0.036 | 0.15 | 0.00
foot | -0.739 | 0.836 | 0.41 | 0.07
torso angle min -0.149, max 0.125 rad; torso height min 1.09, max 1.49 m
foot: on the ground 0.41 of the steps, 16 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 3.14
0.10 | 0.00 | 1.21 | -0.023 | yes | 4.45
0.20 | 0.03 | 1.20 | -0.111 | yes | 5.65
0.30 | 0.11 | 1.18 | -0.133 | yes | 0.68
0.40 | 0.25 | 1.16 | -0.001 | yes | 1.88
0.50 | 0.37 | 1.25 | 0.045 | yes | 3.19
0.60 | 0.40 | 1.39 | -0.017 | no | 4.40
0.70 | 0.44 | 1.42 | -0.019 | no | 5.71
0.80 | 0.49 | 1.34 | -0.020 | no | 0.63
0.90 | 0.55 | 1.18 | -0.007 | yes | 1.94
1.00 | 0.69 | 1.19 | 0.066 | yes | 3.14
1.10 | 0.75 | 1.37 | -0.019 | no | 4.45
1.20 | 0.80 | 1.43 | -0.022 | no | 5.65
1.30 | 0.86 | 1.38 | -0.006 | no | 0.68
1.40 | 0.94 | 1.26 | 0.023 | no | 1.88

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_spring: 0.00
knee_pd_rhythm: 0.00
ankle_balance_speed: 0.08
foot_flat: 0.00

## Round 1: your reply

Round 0 passed comfortably: every practice episode reached d ≥ 3 m, with mean d 6.14 m at about 0.8 m/s. The late falls (around 6.7–7.4 s) still scored 5.9–6.9 m, so speed matters more to the score than these falls. Round 1 makes two small changes and keeps everything else the same, so the effect of each is easy to read:

1. **Push for more speed.** The ankle bias `a2` goes from 0.15 to 0.22. This leans the reference posture further forward, which raises the speed the controller settles at.
2. **Stop the ankle unit saturating.** `ankle_balance_speed` was saturated on 8% of steps, so I widened its declared range from 1.5 to 2.5. It now stays linear through the transients instead of clipping its feedback.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.22},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.3, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

How I'll read the next results:
- **Speed rises and falls stay rare:** I'll push the ankle bias further or increase the knee amplitude.
- **Falls increase:** I'll go back to bias 0.15 and work on torso damping instead.

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 4.82 | 5.04 | height too low
1 | 5.78 | 6.34 | height too low
2 | 3.98 | 3.89 | torso angle out of range
3 | 4.20 | 4.08 | height too low
4 | 4.04 | 3.79 | height too low
5 | 4.67 | 4.72 | height too low
6 | 5.05 | 5.34 | height too low
7 | 4.85 | 5.06 | height too low
8 | 4.42 | 4.47 | torso angle out of range
9 | 4.51 | 4.54 | height too low

Over the 10 episodes: mean d 4.63 m, min 3.98, max 5.78; mean time survived 4.73 s; mean forward speed 0.99 m/s; episodes with d >= 3 m: 10

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.140 | 0.005 | 0.09 | 0.00
leg | -0.583 | 0.033 | 0.15 | 0.00
foot | -0.854 | 0.840 | 0.41 | 0.11
torso angle min -0.134, max 0.193 rad; torso height min 0.71, max 1.44 m
foot: on the ground 0.42 of the steps, 11 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 3.14
0.10 | 0.00 | 1.21 | -0.023 | yes | 4.45
0.20 | 0.04 | 1.21 | -0.102 | yes | 5.65
0.30 | 0.12 | 1.19 | -0.117 | yes | 0.68
0.40 | 0.25 | 1.16 | 0.002 | yes | 1.88
0.50 | 0.37 | 1.24 | 0.051 | yes | 3.19
0.60 | 0.41 | 1.37 | -0.014 | no | 4.40
0.70 | 0.45 | 1.40 | -0.016 | no | 5.71
0.80 | 0.49 | 1.31 | -0.011 | no | 0.63
0.90 | 0.56 | 1.16 | 0.016 | yes | 1.94
1.00 | 0.71 | 1.19 | 0.078 | yes | 3.14
1.10 | 0.78 | 1.37 | -0.014 | no | 4.45
1.20 | 0.84 | 1.44 | -0.014 | no | 5.65
1.30 | 0.91 | 1.39 | 0.001 | no | 0.68
1.40 | 1.00 | 1.27 | 0.032 | no | 1.88

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_spring: 0.00
knee_pd_rhythm: 0.00
ankle_balance_speed: 0.03
foot_flat: 0.00

## Round 2: your reply

# Round 2: back to the round-0 lean, keeping the wider ankle range

**What round 1 showed.** Speed rose (0.80 → 0.99 m/s), but survival fell sharply: mean time survived went from 7.74 s to 4.73 s, and mean d dropped from 6.14 m to 4.63 m. Most falls were "height too low". In seed 0 the thigh folded to −1.14 rad (−0.65 in round 0) and the torso dropped to 0.71 m. The extra forward lean is more than the hip loop can hold. The robot ends up running under itself until the thigh collapses.

**A problem with my round-1 test.** I said I would change things so each effect was easy to read, but I changed two things at once: the ankle bias and the ankle unit's range. So I can't yet say how much of the drop came from the bias and how much from the range.

**Round 2 separates them.** I'm putting the ankle bias back to 0.15 (the round-0 value) and keeping the wider 2.5 range. Everything else matches round 0, so this is a single-variable comparison against round 0:
- **Results close to round 0 (~6.1 m, rare falls):** the bias caused the collapse and the wider range is harmless or helps. Next I'll look for speed through the push-off instead of more lean.
- **Results worse than round 0:** the saturating range was acting as a useful limit on the ankle's authority, and I'll go back to the exact round-0 spec as the base.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.15},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.3, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 4.86 | 8.00 | cut off at 1000 steps
1 | 4.95 | 8.00 | cut off at 1000 steps
2 | 5.16 | 8.00 | cut off at 1000 steps
3 | 5.21 | 8.00 | cut off at 1000 steps
4 | 5.17 | 8.00 | cut off at 1000 steps
5 | 4.92 | 8.00 | cut off at 1000 steps
6 | 5.09 | 8.00 | cut off at 1000 steps
7 | 4.89 | 8.00 | cut off at 1000 steps
8 | 4.71 | 8.00 | cut off at 1000 steps
9 | 4.76 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d 4.97 m, min 4.71, max 5.21; mean time survived 8.00 s; mean forward speed 0.62 m/s; episodes with d >= 3 m: 10

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.421 | 0.010 | 0.08 | 0.00
leg | -0.591 | 0.033 | 0.15 | 0.00
foot | -0.486 | 0.841 | 0.37 | 0.00
torso angle min -0.149, max 0.083 rad; torso height min 1.11, max 1.44 m
foot: on the ground 0.37 of the steps, 16 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 3.14
0.10 | 0.00 | 1.21 | -0.023 | yes | 4.45
0.20 | 0.03 | 1.20 | -0.111 | yes | 5.65
0.30 | 0.11 | 1.18 | -0.133 | yes | 0.68
0.40 | 0.25 | 1.16 | -0.001 | yes | 1.88
0.50 | 0.37 | 1.26 | 0.044 | yes | 3.19
0.60 | 0.40 | 1.40 | -0.019 | no | 4.40
0.70 | 0.44 | 1.43 | -0.020 | no | 5.71
0.80 | 0.48 | 1.35 | -0.029 | no | 0.63
0.90 | 0.55 | 1.19 | -0.019 | yes | 1.94
1.00 | 0.68 | 1.19 | 0.060 | yes | 3.14
1.10 | 0.74 | 1.36 | -0.021 | no | 4.45
1.20 | 0.78 | 1.43 | -0.025 | no | 5.65
1.30 | 0.84 | 1.38 | -0.013 | no | 0.68
1.40 | 0.91 | 1.26 | 0.007 | no | 1.88

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_spring: 0.00
knee_pd_rhythm: 0.00
ankle_balance_speed: 0.00
foot_flat: 0.00

## Round 3: your reply

# Round 3: a middle lean, with the ankle unit kept linear

**What round 2 showed.** With the round-0 bias and the wider ankle range, the robot survived every episode (8.00 s each). But it slowed to 0.62 m/s, so mean d was only 4.97 m, against 6.14 m in round 0.

So the 8% saturation in round 0 was not harmless. It clipped the speed-feedback term (−0.15·ẋ), which let the robot run faster than its linear setpoint. That brought both the speed (0.80 m/s) and the occasional late fall.

**Where the trade-off sits.** With the ankle unit linear (range 2.5), speed rises with the ankle bias, and the two data points are close to a straight line:

| Ankle bias | Speed | Result |
|---|---|---|
| 0.15 | 0.62 m/s | no falls |
| 0.22 | 0.99 m/s | falls at about 4.7 s (thigh folds) |

**Round 3 change.** Ankle bias 0.18, range kept at 2.5. Interpolating gives about 0.78 m/s, close to round 0's speed. If it survives all 8 s, that is about 6.2 m. Unlike round 0, the lean comes from a clean linear term rather than an accidental clip.

How I'll read the result:
- **No or very late falls:** try 0.19–0.20 next.
- **Early collapses:** the stable limit is closer to 0.15, and I fall back to the round-0 spec. It is still the best so far and can be resubmitted as the final design.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.18},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.3, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 6.28 | 8.00 | cut off at 1000 steps
1 | 6.98 | 8.00 | cut off at 1000 steps
2 | 6.34 | 8.00 | cut off at 1000 steps
3 | 5.93 | 6.17 | height too low
4 | 6.44 | 6.98 | torso angle out of range
5 | 6.38 | 6.74 | height too low
6 | 6.07 | 8.00 | cut off at 1000 steps
7 | 6.80 | 7.19 | height too low
8 | 6.38 | 6.88 | torso angle out of range
9 | 5.69 | 6.06 | height too low

Over the 10 episodes: mean d 6.33 m, min 5.69, max 6.98; mean time survived 7.20 s; mean forward speed 0.89 m/s; episodes with d >= 3 m: 10

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.578 | 0.007 | 0.09 | 0.00
leg | -0.589 | 0.035 | 0.15 | 0.00
foot | -0.763 | 0.837 | 0.41 | 0.09
torso angle min -0.143, max 0.121 rad; torso height min 1.07, max 1.49 m
foot: on the ground 0.40 of the steps, 16 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 3.14
0.10 | 0.00 | 1.21 | -0.023 | yes | 4.45
0.20 | 0.03 | 1.20 | -0.107 | yes | 5.65
0.30 | 0.12 | 1.19 | -0.126 | yes | 0.68
0.40 | 0.26 | 1.16 | 0.002 | yes | 1.88
0.50 | 0.38 | 1.24 | 0.048 | yes | 3.19
0.60 | 0.41 | 1.39 | -0.016 | no | 4.40
0.70 | 0.46 | 1.42 | -0.017 | no | 5.71
0.80 | 0.50 | 1.35 | -0.013 | no | 0.63
0.90 | 0.57 | 1.19 | 0.004 | yes | 1.94
1.00 | 0.70 | 1.18 | 0.067 | yes | 3.14
1.10 | 0.76 | 1.36 | -0.016 | no | 4.45
1.20 | 0.81 | 1.42 | -0.020 | no | 5.65
1.30 | 0.87 | 1.37 | -0.003 | no | 0.68
1.40 | 0.95 | 1.26 | 0.028 | no | 1.88

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_spring: 0.00
knee_pd_rhythm: 0.00
ankle_balance_speed: 0.00
foot_flat: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
