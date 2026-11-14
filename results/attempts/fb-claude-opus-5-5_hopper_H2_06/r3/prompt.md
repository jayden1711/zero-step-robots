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

This first design uses one 2 Hz hopping rhythm with PD-style feedback layered on top.

- **Thigh (a0)** does three jobs:
  - It keeps the torso upright. Negative feedback on the torso angle (−3) and its angular velocity (−0.3) holds the torso near a slight forward lean.
  - It regulates speed weakly through −0.1 × x-velocity.
  - It swings the leg forward in flight: +0.3 × sin, which is positive in the quarter cycle after push-off.
- **Leg (a1)** holds a slightly bent knee (about −0.2 rad) with PD feedback. A rhythmic term of 0.5 × cos pushes off near phase 0 and lets the leg compress near phase π.
- **Foot (a2)** has a soft PD towards 0, plus a small push-off term in phase with the leg.
- I put each action in one linear unit with a range of 2. Saturation beyond that range roughly matches the action clip anyway.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": -0.4, "a2": 0.0},
 "units": [
   {"type": "linear", "name": "thigh_balance_swing",
    "inputs": {"obs[1]": -3.0, "obs[7]": -0.3, "obs[5]": -0.1, "sin(hop)": 0.3},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd_push",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.5},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd_push",
    "inputs": {"obs[4]": -1.0, "obs[10]": -0.05, "cos(hop)": 0.2},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.03 | 0.26 | torso angle out of range
1 | -0.03 | 0.26 | torso angle out of range
2 | -0.04 | 0.27 | torso angle out of range
3 | -0.04 | 0.27 | torso angle out of range
4 | -0.04 | 0.27 | torso angle out of range
5 | -0.04 | 0.27 | torso angle out of range
6 | -0.03 | 0.26 | torso angle out of range
7 | -0.04 | 0.27 | torso angle out of range
8 | -0.03 | 0.26 | torso angle out of range
9 | -0.03 | 0.26 | torso angle out of range

Over the 10 episodes: mean d -0.04 m, min -0.04, max -0.03; mean time survived 0.27 s; mean forward speed -0.13 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.004 | 0.69 | 0.33
leg | -0.353 | 0.003 | 0.10 | 0.00
foot | 0.004 | 0.087 | 0.14 | 0.00
torso angle min -0.190, max 0.003 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.73 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.21 | -0.005 | yes | 1.31
0.20 | -0.00 | 1.21 | -0.095 | yes | 2.51

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thigh_balance_swing: 0.00
leg_pd_push: 0.00
foot_pd_push: 0.00

## Round 1: your reply

Round 0 fell over backward in about 0.27 s. The cause was posture geometry, not the feedback sign.

**What went wrong in round 0**
- The thigh joint sat pinned at its upper limit of 0 for the whole episode (min −0.005, max 0.004). The torso feedback was pushing positive torque into that limit, and a joint at its limit cannot move further that way, so the feedback had no effect.
- The leg bias of −0.4 bent the knee to about −0.35 rad. With the thigh pinned straight, the thigh and torso move as one rigid body. To keep the foot under the body, that body has to tilt back by roughly 0.53 × the knee bend. That predicts −0.19 rad, which is exactly the torso angle we saw.
- So this robot can only bend its knee if the thigh angle sits below 0. Otherwise the torso is forced backward.

**What changes in round 1**
- **Knee (a1):** a PD hold near straight (about −0.1 rad), with only a small rhythmic term (0.2 × cos). This keeps the forced backward tilt small.
- **Thigh (a0):** the same balance feedback on torso angle and angular velocity (−3 and −0.3). I dropped the positive bias that pushed the thigh into its limit, and added a small negative term on the thigh angle itself (−0.3 × obs[2]) so it hovers slightly below 0, where torque can act both ways. The forward swing is 0.2 × sin.
- **Foot (a2):** acts as an ankle balance controller. It has a soft PD on the foot angle, and its torque rises with forward speed (0.3 × obs[5]) with an offset that sets a target speed of about 0.5 m/s. When the robot is slower than that, the foot tips the leg forward; when faster, it pushes back. A small push-off term follows the hop rhythm.
- **Rhythm:** 2.5 Hz with smaller amplitudes than round 0. This round's main job is to survive and confirm the balance loop works.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": -0.15},
 "units": [
   {"type": "linear", "name": "thigh_balance_swing",
    "inputs": {"obs[1]": -3.0, "obs[7]": -0.3, "obs[2]": -0.3, "sin(hop)": 0.2},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_push",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.2},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed",
    "inputs": {"obs[4]": -1.0, "obs[10]": -0.05, "obs[5]": 0.3, "cos(hop)": 0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.14 | 0.26 | torso angle out of range
1 | -0.14 | 0.26 | torso angle out of range
2 | -0.14 | 0.26 | torso angle out of range
3 | -0.14 | 0.26 | torso angle out of range
4 | -0.15 | 0.26 | torso angle out of range
5 | -0.14 | 0.26 | torso angle out of range
6 | -0.14 | 0.26 | torso angle out of range
7 | -0.16 | 0.26 | torso angle out of range
8 | -0.14 | 0.26 | torso angle out of range
9 | -0.14 | 0.26 | torso angle out of range

Over the 10 episodes: mean d -0.14 m, min -0.16, max -0.14; mean time survived 0.26 s; mean forward speed -0.55 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.003 | 0.46 | 0.03
leg | -0.136 | 0.003 | 0.10 | 0.00
foot | -0.215 | 0.004 | 0.24 | 0.00
torso angle min -0.193, max -0.001 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.69 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | -0.01 | 1.20 | -0.012 | yes | 1.63
0.20 | -0.07 | 1.21 | -0.108 | yes | 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thigh_balance_swing: 0.00
knee_pd_push: 0.00
ankle_balance_speed: 0.00

## Round 2: your reply

# Round 2 design

## What went wrong in rounds 0–1

The −0.19 rad torso angle in round 0 was not a static geometry match. It was the last value before the episode ended at the 0.2 limit, so my round-1 explanation was incomplete. Three things together explain both rounds:

1. **The hip joint was pinned.** The thigh angle stayed at 0, which is its upper limit. When the torso fell backward, the feedback asked for positive thigh torque, but that only pushed into the limit. The hip therefore had no effect on the torso in either round.

2. **The ankle bias pushed the robot backward.** With the foot on the ground, negative foot torque tips the leg's top backward. Round 1's ankle bias of −0.15 did exactly that: the foot angle went to −0.215 and the torso fell back.

3. **The gains were far too high.** The actuators are strong (gear 200, so 0.1 of action is about 20 Nm). A torso damping of 0.3 gives a discrete-time loop gain above 2 at 0.008 s per step, which makes the loop unstable. Round 0's thigh torque was saturated on 33% of steps, which fits that.

**Geometry constraint.** The hip and knee can only swing the lower part backward. So to keep the hip off its limit with the torso upright, the leg itself has to tip top-forward, with the ankle behind the hip. The forward-pointing foot supports that posture: the toe reaches 0.26 m ahead of the ankle.

## Round 2 plan: get a working balance loop first, with a gentle bounce

| Joint | Controller |
|---|---|
| **Hip (a0)** | Keeps the torso upright: −1.0·obs[1] − 0.05·obs[7]. These gains are about 3–6× lower than before and are stable at this step size. |
| **Ankle (a2)** | Controls the absolute angle of the leg, `θ_leg = −obs[1] + obs[2] + obs[3]`, towards −0.35 (top tipped forward), with damping on its rate. It is a reflex unit with output capped at ±0.15, so it never tips the foot onto its heel or toe. A bias of −0.06 carries the static weight in front of the ankle. Holding the leg tipped forward is what keeps the thigh near −0.15 rad, away from its limit. |
| **Knee (a1)** | Moderate PD to −0.2 rad, which leaves room to extend. A small 2.5 Hz rhythm (0.25 × cos) tests whether the robot bounces without losing balance. |

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.4, "a2": -0.06},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": -1.0, "obs[7]": -0.05},
    "range": 0.6, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_bounce",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.25},
    "range": 1.2, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "ankle_leg_angle_pd",
    "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.2, "obs[8]": 0.2, "obs[9]": 0.2},
    "threshold": -0.35, "sharpness": 6.67, "to": {"a2": 0.15}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 1.51 | 2.70 | height too low
1 | 1.52 | 2.70 | height too low
2 | 1.49 | 2.70 | height too low
3 | 1.50 | 2.71 | height too low
4 | 1.49 | 2.71 | height too low
5 | 1.50 | 2.71 | height too low
6 | 1.51 | 2.70 | height too low
7 | 1.49 | 2.70 | height too low
8 | 1.52 | 2.71 | height too low
9 | 1.51 | 2.70 | height too low

Over the 10 episodes: mean d 1.50 m, min 1.49, max 1.52; mean time survived 2.71 s; mean forward speed 0.56 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.059 | 0.002 | 0.08 | 0.00
leg | -0.385 | 0.003 | 0.16 | 0.00
foot | -0.822 | 0.589 | 0.15 | 0.00
torso angle min -0.167, max 0.114 rad; torso height min 0.70, max 1.25 m
foot: on the ground 0.93 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | -0.01 | 1.20 | -0.045 | yes | 1.63
0.20 | -0.01 | 1.20 | -0.134 | yes | 3.14
0.30 | -0.01 | 1.19 | -0.159 | yes | 4.78
0.40 | 0.05 | 1.20 | -0.042 | yes | 0.00
0.50 | 0.14 | 1.20 | 0.036 | yes | 1.63
0.60 | 0.18 | 1.19 | -0.032 | yes | 3.14
0.70 | 0.20 | 1.18 | -0.017 | yes | 4.78
0.80 | 0.25 | 1.17 | 0.070 | yes | 6.28
0.90 | 0.32 | 1.16 | 0.037 | yes | 1.63
1.00 | 0.34 | 1.15 | -0.081 | yes | 3.14
1.10 | 0.37 | 1.16 | -0.042 | yes | 4.78
1.20 | 0.41 | 1.15 | 0.092 | yes | 6.28
1.30 | 0.43 | 1.11 | 0.042 | yes | 1.63
1.40 | 0.43 | 1.10 | -0.095 | yes | 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
hip_torso_pd: 0.00
knee_pd_bounce: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
