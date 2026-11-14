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

This first design is conservative. It puts strong upright balance and joint posture holding on top of a moderate 2 Hz hop rhythm. The practice results will show whether the robot stays up and moves forward before I make the gait more aggressive.

- **Balance (thigh, a0):** a0 gets −3·(obs[1] + 0.15·obs[7] + 0.03·obs[5]) plus a bias of +0.15.
  - The torso-angle and angular-velocity terms push against any lean, as the hint says (negative thigh torque pitches the torso back).
  - The bias settles the torso at a slight forward lean (about 0.05 rad), which drives forward motion.
  - The forward-speed term (obs[5]) leans the torso back as speed rises, which limits speed.
- **Rhythm (one oscillator at 2 Hz):** when sin(phase) > 0 the robot is in stance.
  - The leg extends (a1 > 0) and the foot pushes toes-down (a2 > 0).
  - The thigh sweeps backward (a0 < 0), driving the body forward.
  - In the other half-cycle (flight) the signs reverse, so the thigh swings forward and the leg folds.
- **Posture (spring-damper holds on each joint):**
  - The leg is held straight.
  - The foot is held flat.
  - The thigh is weakly held near −0.2 rad.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15, "obs[5]": 0.03},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.25, "a1": 0.4, "a2": 0.3}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -0.5}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": 1.0, "obs[8]": 0.05},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.3}}
 ],
 "bias_note_unused": null}
```

Wait, the block must hold only the spec, so here is the clean version to use:

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.09},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15, "obs[5]": 0.03},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.25, "a1": 0.4, "a2": 0.3}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -0.5}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": 1.0, "obs[8]": 0.05},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.3}}
 ]}
```

Two changes in the clean version:
- I dropped the extra field.
- I lowered the a0 bias to 0.09. The thigh posture term adds +0.06 to a0 at the −0.2 rad thigh target, so the total offset is about the same as before.

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 1.11 | 1.83 | height too low
1 | 1.12 | 1.86 | height too low
2 | 1.09 | 1.81 | height too low
3 | 1.10 | 1.81 | height too low
4 | 1.12 | 1.78 | height too low
5 | 1.10 | 1.82 | height too low
6 | 1.11 | 1.83 | height too low
7 | 1.09 | 1.82 | height too low
8 | 1.11 | 1.86 | height too low
9 | 1.11 | 1.83 | height too low

Over the 10 episodes: mean d 1.11 m, min 1.09, max 1.12; mean time survived 1.83 s; mean forward speed 0.61 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -1.181 | 0.011 | 0.09 | 0.00
leg | -0.274 | 0.031 | 0.19 | 0.00
foot | -0.036 | 0.616 | 0.21 | 0.00
torso angle min -0.029, max 0.096 rad; torso height min 0.71, max 1.27 m
foot: on the ground 0.82 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | -0.008 | yes | 1.31
0.20 | 0.06 | 1.21 | -0.028 | yes | 2.51
0.30 | 0.14 | 1.20 | -0.009 | yes | 3.82
0.40 | 0.18 | 1.22 | 0.035 | yes | 5.03
0.50 | 0.18 | 1.26 | 0.018 | yes | 0.05
0.60 | 0.20 | 1.25 | 0.023 | no | 1.26
0.70 | 0.23 | 1.17 | -0.016 | yes | 2.56
0.80 | 0.31 | 1.16 | 0.007 | yes | 3.77
0.90 | 0.37 | 1.19 | 0.051 | yes | 5.08
1.00 | 0.40 | 1.25 | 0.075 | yes | 0.00
1.10 | 0.46 | 1.24 | 0.059 | no | 1.31
1.20 | 0.51 | 1.14 | 0.012 | yes | 2.51
1.30 | 0.57 | 1.03 | 0.038 | yes | 3.82
1.40 | 0.64 | 1.04 | 0.078 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
hop_rhythm: 0.00
leg_pd: 0.00
foot_pd: 0.00
thigh_posture: 0.00

## Now: round 1 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
