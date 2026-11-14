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

Round 0 is a conservative baseline. The aim is to stay upright for the full 1000 steps and creep forward. Later rounds can raise the hop amplitude once I see how it fails.

**Design**
- **Oscillator:** one 2 Hz oscillator, `hop`.
- **Torso balance at the thigh:** `a0 = -2.0·(obs[1] - 0.05) - 0.3·obs[7]`. The 0.05 rad target lean, written as bias +0.1, is what drives forward speed. A weak thigh-angle term keeps the hip from drifting.
- **Leg posture hold:** proportional-derivative (PD) control holds the leg joint near straight with a slight bend, and holds the foot near neutral. The leg term is `-1.5·(obs[3] + 0.1)`, written as bias -0.15.
- **Rhythm:**
  - `cos(hop)` drives leg compression and extension (a1) and foot push-off (a2).
  - `sin(hop)` drives the thigh swing (a0), so the thigh runs a quarter cycle ahead of the leg.
  - Amplitudes are moderate (0.3–0.4), so the posture loops dominate at first.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": -0.15},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.5, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.4, "a2": 0.3}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.05 | 0.34 | torso angle out of range
1 | -0.05 | 0.34 | torso angle out of range
2 | -0.06 | 0.34 | torso angle out of range
3 | -0.06 | 0.34 | torso angle out of range
4 | -0.06 | 0.34 | torso angle out of range
5 | -0.06 | 0.34 | torso angle out of range
6 | -0.05 | 0.34 | torso angle out of range
7 | -0.07 | 0.34 | torso angle out of range
8 | -0.05 | 0.33 | torso angle out of range
9 | -0.05 | 0.34 | torso angle out of range

Over the 10 episodes: mean d -0.06 m, min -0.07, max -0.05; mean time survived 0.34 s; mean forward speed -0.17 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.005 | 0.003 | 0.46 | 0.00
leg | -0.300 | 0.003 | 0.13 | 0.00
foot | -0.060 | 0.096 | 0.13 | 0.00
torso angle min -0.192, max 0.005 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.79 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.005 | yes | 1.31
0.20 | 0.02 | 1.21 | -0.025 | yes | 2.51
0.30 | -0.03 | 1.23 | -0.162 | yes | 3.82

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_posture: 0.00
leg_pd: 0.00
foot_pd: 0.00
rhythm_cos: 0.00
rhythm_sin: 0.00

## Round 1: your reply

## Round 0 diagnosis

- **The thigh was pinned at its joint limit.** The thigh angle stayed in [-0.005, 0.003] even though mean |a0| was 0.46. The thigh's upper limit is 0, so the positive a0 that should have corrected the backward lean only pressed the joint against its stop. The thigh balance loop had no effect.
- **The robot tipped over its foot as one rigid stick.** The torso angle reached -0.19 while the thigh angle stayed at 0, and x moved backward. That points to ankle torque. In the late part of the cycle, cos(hop) was about -1, so the rhythm sent a2 ≈ -0.3. The foot PD added more negative torque as the foot angle rose to +0.1. With the foot planted, negative a2 tips the leg, and everything above it, backward. The negative leg torque (bending to -0.3) also pushed the same way.

## Changes for round 1

- **Thigh off its limit:** the posture target is now -0.1, so the torso PD can act in both directions. The torso PD is stiffer: -3·obs[1] - 0.4·obs[7].
- **Ankle-strategy balance (new unit):** `a2 += -2·obs[1] - 0.3·obs[7] - 0.3·(obs[5] - 0.4)`.
  - Leaning backward or moving backward gives positive foot torque, which tips the body forward.
  - The obs[5] term regulates forward speed towards 0.4 m/s.
- **Foot rhythm removed.** The foot PD is weaker, so it doesn't fight the balance unit.
- **Leg and thigh rhythm reduced** to 0.25 and 0.15 until survival is established.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": 0.12},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3, "obs[5]": -0.3},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.25}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.15}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.14 | 8.00 | cut off at 1000 steps
1 | 0.14 | 8.00 | cut off at 1000 steps
2 | 0.13 | 8.00 | cut off at 1000 steps
3 | 0.13 | 8.00 | cut off at 1000 steps
4 | 0.12 | 8.00 | cut off at 1000 steps
5 | 0.13 | 8.00 | cut off at 1000 steps
6 | 0.13 | 8.00 | cut off at 1000 steps
7 | 0.12 | 8.00 | cut off at 1000 steps
8 | 0.14 | 8.00 | cut off at 1000 steps
9 | 0.14 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d 0.13 m, min 0.12, max 0.14; mean time survived 8.00 s; mean forward speed 0.02 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.155 | 0.008 | 0.10 | 0.00
leg | -0.282 | 0.016 | 0.11 | 0.00
foot | 0.004 | 0.306 | 0.12 | 0.00
torso angle min -0.064, max 0.036 rad; torso height min 1.19, max 1.25 m
foot: on the ground 0.99 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | -0.004 | yes | 1.31
0.20 | 0.02 | 1.20 | -0.040 | yes | 2.51
0.30 | 0.06 | 1.20 | -0.060 | yes | 3.82
0.40 | 0.10 | 1.20 | -0.032 | yes | 5.03
0.50 | 0.13 | 1.20 | -0.009 | yes | 0.05
0.60 | 0.12 | 1.20 | 0.025 | yes | 1.26
0.70 | 0.10 | 1.20 | 0.032 | yes | 2.56
0.80 | 0.08 | 1.20 | -0.042 | yes | 3.77
0.90 | 0.12 | 1.19 | -0.028 | yes | 5.08
1.00 | 0.14 | 1.20 | -0.007 | yes | 0.00
1.10 | 0.13 | 1.20 | 0.026 | yes | 1.31
1.20 | 0.10 | 1.20 | 0.033 | yes | 2.51
1.30 | 0.08 | 1.20 | -0.043 | yes | 3.82
1.40 | 0.11 | 1.19 | -0.030 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_posture: 0.00
leg_pd: 0.00
foot_pd: 0.00
ankle_balance: 0.00
rhythm_cos: 0.00
rhythm_sin: 0.00

## Round 2: your reply

## Round 1 diagnosis

- **Balance works.** The robot survived all 10 episodes for the full 8 s. Torso angle stayed within ±0.065 rad, and no unit saturated.
- **It never moved forward.**
  - The foot was on the ground 99% of the time, with one touchdown, so the robot never left the ground.
  - x swayed back and forth by about ±0.03 m in step with the 2 Hz rhythm: forward while the torso pitched back, back while it pitched forward. The net result was d ≈ 0.13 m.
  - A one-legged robot cannot make net progress while its foot stays planted, so the gait needs real flight phases.

## Changes for round 2

1. **Stronger leg rhythm (a1: 0.25 → 0.6).** With the joint bent near -0.28 rad at most, the leg could not push hard enough to leave the ground. Positive cos(hop) now extends the leg sharply (push-off), and negative cos(hop) compresses it.
2. **Foot push-off in phase with leg extension (a2 += 0.3·cos).** Positive foot torque in stance tips the body forward, which adds forward impulse during push-off.
3. **Thigh drives propulsion (new).** The thigh now gets `-0.3·cos(hop)`, in phase with leg extension. In stance this sweeps the leg backward and pushes the body forward. When cos(hop) < 0 (flight and compression), the thigh torque turns positive and returns the leg towards 0, the forward position, ready for landing. A small `sin` term (0.1) is kept for swing timing.
4. **Thigh posture and leg damping unchanged.** The thigh posture target stays at -0.1. Leg PD damping is slightly higher, so landings don't buckle the leg.
5. **Balance loops unchanged, with a stronger push towards speed.** The ankle speed term rises to -0.4·(obs[5] - 0.5), written as bias +0.2 on a2 together with the existing offset. This pushes harder for forward motion.

This round is deliberately more aggressive. Surviving in place scores about 0, so I would rather learn how a real hop fails and tune it back.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": 0.2},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3, "obs[5]": -0.4},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.3, "a1": 0.6, "a2": 0.3}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 5.43 | 8.00 | cut off at 1000 steps
1 | 5.43 | 8.00 | cut off at 1000 steps
2 | 5.43 | 8.00 | cut off at 1000 steps
3 | 5.43 | 8.00 | cut off at 1000 steps
4 | 5.44 | 8.00 | cut off at 1000 steps
5 | 5.43 | 8.00 | cut off at 1000 steps
6 | 5.43 | 8.00 | cut off at 1000 steps
7 | 5.44 | 8.00 | cut off at 1000 steps
8 | 5.43 | 8.00 | cut off at 1000 steps
9 | 5.44 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d 5.43 m, min 5.43, max 5.44; mean time survived 8.00 s; mean forward speed 0.68 m/s; episodes with d >= 3 m: 10

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.318 | 0.014 | 0.11 | 0.00
leg | -0.374 | 0.023 | 0.21 | 0.00
foot | -0.628 | 0.390 | 0.32 | 0.00
torso angle min -0.114, max 0.101 rad; torso height min 1.14, max 1.41 m
foot: on the ground 0.50 of the steps, 16 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.02 | 1.22 | -0.022 | yes | 1.31
0.20 | 0.05 | 1.22 | 0.004 | no | 2.51
0.30 | 0.04 | 1.19 | -0.101 | yes | 3.82
0.40 | 0.08 | 1.19 | -0.077 | yes | 5.03
0.50 | 0.14 | 1.20 | -0.049 | yes | 0.05
0.60 | 0.20 | 1.19 | -0.019 | yes | 1.26
0.70 | 0.23 | 1.21 | 0.042 | yes | 2.56
0.80 | 0.22 | 1.27 | 0.039 | yes | 3.77
0.90 | 0.21 | 1.26 | 0.001 | no | 5.08
1.00 | 0.24 | 1.18 | -0.011 | yes | 0.00
1.10 | 0.33 | 1.18 | 0.004 | yes | 1.31
1.20 | 0.37 | 1.23 | 0.056 | yes | 2.51
1.30 | 0.37 | 1.31 | 0.074 | yes | 3.82
1.40 | 0.39 | 1.31 | 0.043 | no | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_posture: 0.00
leg_pd: 0.00
foot_pd: 0.00
ankle_balance: 0.00
rhythm_cos: 0.00
rhythm_sin: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
