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

This first design is a conservative hopping gait with strong posture control. The idea is to stay healthy first, then make progress forward.

**How the controller is built**
- **Oscillator:** one oscillator, "hop", runs at 2 Hz.
- **Torso balance (thigh, a0):** the thigh torque is −3·(torso angle + 0.15·torso angular velocity). This opposes both lean and pitch rate, as the hint says.
- **Lean and speed (thigh, a0):** a bias of +0.2 sets a slight forward lean. A small −0.2·x-velocity term leans the torso back when the robot goes too fast.
- **Leg and foot holding (a1, a2):** proportional-derivative (PD) control holds the leg joint at about −0.1 rad (slightly bent) and the foot at 0. This keeps the leg from collapsing.
- **Rhythm:**
  - The thigh swings with 0.3·cos.
  - The leg compresses and extends with 0.5·sin.
  - The foot pushes off with 0.3·sin, in phase with the leg.
  - The thigh swing leads the leg extension by a quarter cycle.
- **Rhythm size:** the rhythm amplitudes are kept moderate so the posture feedback stays in control. I'll scale them up once I see whether the robot stays upright.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.2, "a1": -0.2},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 0.6, "tol": 0.05, "to": {"a0": -3.0}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -2.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.5, "a2": 0.3}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.03 | 0.96 | torso angle out of range
1 | -0.03 | 0.96 | torso angle out of range
2 | -0.05 | 0.95 | torso angle out of range
3 | -0.04 | 0.95 | torso angle out of range
4 | -0.05 | 0.95 | torso angle out of range
5 | -0.04 | 0.95 | torso angle out of range
6 | -0.03 | 0.96 | torso angle out of range
7 | -0.05 | 0.94 | torso angle out of range
8 | -0.03 | 0.96 | torso angle out of range
9 | -0.03 | 0.96 | torso angle out of range

Over the 10 episodes: mean d -0.04 m, min -0.05, max -0.03; mean time survived 0.96 s; mean forward speed -0.04 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.112 | 0.018 | 0.36 | 0.20
leg | -0.335 | 0.022 | 0.17 | 0.00
foot | -0.087 | 0.087 | 0.15 | 0.00
torso angle min -0.197, max 0.017 rad; torso height min 1.20, max 1.26 m
foot: on the ground 0.84 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.006 | yes | 1.31
0.20 | 0.05 | 1.20 | 0.010 | yes | 2.51
0.30 | 0.09 | 1.21 | -0.032 | yes | 3.82
0.40 | 0.07 | 1.24 | -0.051 | yes | 5.03
0.50 | 0.02 | 1.26 | -0.137 | yes | 0.05
0.60 | 0.02 | 1.21 | -0.020 | yes | 1.26
0.70 | 0.03 | 1.21 | -0.002 | yes | 2.56
0.80 | 0.05 | 1.21 | -0.029 | yes | 3.77
0.90 | 0.00 | 1.23 | -0.128 | yes | 5.08

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
speed_reg: 0.00
leg_pd: 0.00
foot_pd: 0.00
thigh_rhythm: 0.00
leg_rhythm: 0.00

## Round 1: your reply

Round 0 fell backward after about 0.95 s in every episode. Two things in the data point to the cause:

- **The thigh was jammed against its upper limit.** It reached a maximum of +0.018 rad against a 0 limit, and a0 was saturated positive on 20% of steps. A positive thigh torque only pitches the torso forward if the thigh can still rotate. Pinned at the limit, torso and leg move as one rigid stick, so the hip loses its forward-correcting authority.
- **The leg rhythm itself caused the backward pitch.** The torso dipped at phase ≈ 5–0 (−0.137, then −0.128), right after sin(hop) is most negative. With the foot planted, a negative leg torque pitches the thigh backward, and through the locked hip the torso too. The −0.2 bias on a1 made this worse.

**Changes for round 1:**

- **Balance through the ankle too.** With the foot flat on the ground, a positive foot torque pitches the whole body forward, the same sign logic as the thigh. So the torso-balance unit now also drives a2 (gain −1.5). This works even when the thigh is at its limit, because the long, heavy foot can shift the centre of pressure.
- **Stronger damping.** The angular-velocity weight goes from 0.15 to 0.2.
- **Small forward-lean target.** Positive biases on a0 and a2 aim for a torso angle of about +0.05.
- **Straighter leg.** The a1 bias is now slightly positive. The leg PD is stiffer and targets about 0 (straight). The leg rhythm is cut to 0.3, so leg flexion no longer throws the torso back.
- **Rhythm and foot push-off.** The foot gets a small sin component for toe push-off. The thigh swing (0.3·cos) and speed regulation are kept.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.15, "a1": 0.1, "a2": 0.08},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 0.8, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -3.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.3, "a2": 0.2}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.08 | 8.00 | cut off at 1000 steps
1 | 0.10 | 8.00 | cut off at 1000 steps
2 | 0.07 | 8.00 | cut off at 1000 steps
3 | 0.08 | 8.00 | cut off at 1000 steps
4 | 0.06 | 8.00 | cut off at 1000 steps
5 | 0.08 | 8.00 | cut off at 1000 steps
6 | 0.08 | 8.00 | cut off at 1000 steps
7 | 0.07 | 8.00 | cut off at 1000 steps
8 | 0.09 | 8.00 | cut off at 1000 steps
9 | 0.09 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d 0.08 m, min 0.06, max 0.10; mean time survived 8.00 s; mean forward speed 0.01 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.400 | 0.009 | 0.09 | 0.00
leg | -0.040 | 0.007 | 0.16 | 0.00
foot | -0.139 | 0.421 | 0.17 | 0.00
torso angle min -0.047, max 0.104 rad; torso height min 1.12, max 1.28 m
foot: on the ground 0.98 of the steps, 7 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.20 | 0.006 | yes | 1.31
0.20 | 0.05 | 1.21 | 0.002 | yes | 2.51
0.30 | 0.14 | 1.20 | -0.039 | yes | 3.82
0.40 | 0.22 | 1.19 | -0.040 | yes | 5.03
0.50 | 0.27 | 1.21 | 0.016 | yes | 0.05
0.60 | 0.30 | 1.23 | 0.051 | yes | 1.26
0.70 | 0.32 | 1.19 | 0.037 | yes | 2.56
0.80 | 0.34 | 1.14 | 0.001 | yes | 3.77
0.90 | 0.36 | 1.16 | -0.003 | yes | 5.08
1.00 | 0.37 | 1.23 | 0.046 | yes | 0.00
1.10 | 0.37 | 1.26 | 0.080 | yes | 1.31
1.20 | 0.38 | 1.22 | 0.061 | yes | 2.51
1.30 | 0.37 | 1.13 | 0.017 | yes | 3.82
1.40 | 0.39 | 1.14 | 0.011 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
speed_reg: 0.00
leg_pd: 0.00
foot_pd: 0.00
thigh_rhythm: 0.00
leg_rhythm: 0.00

## Round 2: your reply

Round 1 fixed the falls: all 10 episodes lasted the full 8 s. But the robot barely moved. It covered about 0.08 m, with the foot on the ground 98% of the time and the leg almost locked (−0.04 to 0 rad). The posture control is now strong enough that the rhythm can't produce hops or any forward drift. Round 2 keeps the balance structure and adds drive:

- **Stronger rhythm:**
  - Thigh swing goes from 0.3 to 0.45·cos.
  - Leg extension goes from 0.3 to 0.6·sin.
  - Foot push-off goes from 0.2 to 0.4·sin.

  This should give real compression and push-off, and lift the foot off the ground.
- **Softer leg PD:** the gain drops from −3 to −2. The rhythm was being cancelled: the leg moved only 0.04 rad.
- **More forward lean:**
  - The a0 bias goes from 0.15 to 0.25 and the a2 bias from 0.08 to 0.1. This sets a lean target of about 0.07–0.08 rad, still well inside the 0.2 limit.
  - Speed regulation goes from −0.2 to −0.25·vx. At about 1 m/s this cancels the extra lean drive, so the robot leans forward only while it is slow.
- **Torso damping:** the angular-velocity weight goes from 0.2 to 0.25, for headroom against the bigger rhythm.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.25, "a1": 0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 1.0, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.25}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.45}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.4}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 1.53 | 1.79 | height too low
1 | 1.47 | 1.82 | height too low
2 | 1.57 | 1.72 | height too low
3 | 1.57 | 1.74 | height too low
4 | 1.57 | 1.69 | height too low
5 | 1.55 | 1.77 | height too low
6 | 1.52 | 1.79 | height too low
7 | 1.55 | 1.77 | height too low
8 | 1.46 | 1.82 | height too low
9 | 1.52 | 1.80 | height too low

Over the 10 episodes: mean d 1.53 m, min 1.46, max 1.57; mean time survived 1.77 s; mean forward speed 0.87 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.331 | 0.008 | 0.10 | 0.00
leg | -0.182 | 0.027 | 0.31 | 0.00
foot | -0.265 | 0.700 | 0.32 | 0.00
torso angle min -0.062, max 0.084 rad; torso height min 0.71, max 1.31 m
foot: on the ground 0.57 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.010 | yes | 1.31
0.20 | 0.07 | 1.22 | 0.007 | yes | 2.51
0.30 | 0.15 | 1.22 | -0.041 | yes | 3.82
0.40 | 0.22 | 1.19 | -0.039 | yes | 5.03
0.50 | 0.25 | 1.28 | 0.041 | yes | 0.05
0.60 | 0.27 | 1.31 | 0.081 | no | 1.26
0.70 | 0.29 | 1.23 | 0.064 | no | 2.56
0.80 | 0.36 | 1.15 | 0.007 | yes | 3.77
0.90 | 0.45 | 1.17 | -0.013 | yes | 5.08
1.00 | 0.53 | 1.26 | 0.039 | yes | 0.00
1.10 | 0.62 | 1.28 | 0.065 | no | 1.31
1.20 | 0.70 | 1.19 | 0.038 | no | 2.51
1.30 | 0.78 | 0.99 | -0.016 | yes | 3.82
1.40 | 0.90 | 0.95 | -0.035 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
speed_reg: 0.00
leg_pd: 0.00
foot_pd: 0.00
thigh_rhythm: 0.00
leg_rhythm: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
