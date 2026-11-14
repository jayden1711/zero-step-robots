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

Round 0 design: one 2 Hz hop oscillator, PD balance at the thigh, posture PD at each joint, and moderate rhythmic torques. Amplitudes are deliberately conservative so the first results show whether the rhythm moves the robot forward or knocks it over.

**How it works:**
- **Oscillator `hop`:** runs at 2.0 Hz, starting at phase 0.
- **Rhythm:**
  - `sin(hop)` drives the leg extension and compression: 0.45 to the leg joint and 0.35 to the foot.
  - `cos(hop)` drives the thigh swing, 90° out of phase with the push: 0.3 to the thigh.
- **Torso balance at the thigh:**
  - The thigh torque is a0 = −5·obs[1] − 0.5·obs[7] − 0.1·obs[5] + 0.2.
  - The +0.2 bias makes the controller hold a torso lean of about 0.04 rad forward, which drives forward motion.
  - The −0.1·obs[5] term reduces that lean as forward speed rises, which limits speed.
- **Posture:**
  - The leg and foot joints have weak PD pulls toward 0 (straight), so the rhythm moves them around a neutral pose.
  - The thigh has a lighter PD so it doesn't fight the balance term.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5, "obs[5]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_posture", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_posture", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "push_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a1": 0.45, "a2": 0.35}},
   {"type": "linear", "name": "swing_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.20 | 1.82 | torso angle out of range
1 | -0.19 | 1.82 | torso angle out of range
2 | -0.22 | 1.81 | torso angle out of range
3 | -0.22 | 1.80 | torso angle out of range
4 | -0.22 | 1.80 | torso angle out of range
5 | -0.21 | 1.81 | torso angle out of range
6 | -0.20 | 1.82 | torso angle out of range
7 | -0.22 | 1.81 | torso angle out of range
8 | -0.20 | 1.82 | torso angle out of range
9 | -0.20 | 1.82 | torso angle out of range

Over the 10 episodes: mean d -0.21 m, min -0.22, max -0.19; mean time survived 1.81 s; mean forward speed -0.12 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.115 | 0.016 | 0.41 | 0.18
leg | -0.190 | 0.024 | 0.21 | 0.00
foot | -0.108 | 0.128 | 0.14 | 0.00
torso angle min -0.193, max 0.042 rad; torso height min 1.19, max 1.27 m
foot: on the ground 0.88 of the steps, 4 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.005 | yes | 1.31
0.20 | 0.05 | 1.21 | 0.014 | yes | 2.51
0.30 | 0.12 | 1.21 | -0.000 | yes | 3.82
0.40 | 0.12 | 1.24 | 0.012 | yes | 5.03
0.50 | 0.08 | 1.27 | -0.021 | yes | 0.05
0.60 | 0.08 | 1.21 | 0.039 | yes | 1.26
0.70 | 0.10 | 1.20 | 0.032 | yes | 2.56
0.80 | 0.13 | 1.20 | 0.009 | yes | 3.77
0.90 | 0.10 | 1.24 | 0.014 | yes | 5.08
1.00 | 0.04 | 1.26 | -0.068 | yes | 0.00
1.10 | 0.01 | 1.20 | -0.002 | yes | 1.31
1.20 | 0.01 | 1.22 | -0.009 | yes | 2.51
1.30 | 0.03 | 1.21 | -0.018 | yes | 3.82
1.40 | -0.01 | 1.22 | -0.088 | yes | 5.03

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_posture: 0.00
leg_posture: 0.00
foot_posture: 0.00
push_rhythm: 0.00
swing_rhythm: 0.00

## Round 1: your reply

Round 0 never really hopped and fell backward. The foot was on the ground 88% of the time with only 4 touchdowns, and the leg bent by only about 0.19 rad. The thigh swing pushed the body forward and back about equally, then the whole body tipped backward.

**What the data shows:**
- **Balance sign is right.** The torso feedback did stabilise the torso for about 1.8 s. With 200× actuator gearing, a wrong sign would have tipped it over almost at once, so I keep the sign.
- **The rhythm is phased correctly.** x rose while the thigh swung back (phase about 1.3 to 3.8) and fell while it swung forward. The fix is to unload the leg during the forward swing.
- **The leg needs a real push-off.** The leg posture spring (gain 2) capped the leg rhythm at about ±0.2 rad. Thrust has to be much stronger.

**Changes in round 1:**
- **Leg thrust:** the leg rhythm becomes a near square-wave reflex, 0.7·tanh(3·sin), on the leg joint. It flexes hard and then extends hard. The leg spring is softer (1.5) and a −0.1 leg bias keeps the knee slightly bent.
- **Foot push:** the foot gets a smaller push (0.3) in the same phase as the leg.
- **Cycle frequency:** raised to 2.5 Hz for a brisker hop.
- **Thigh:** the swing rises to 0.35 on cos. The thigh posture spring is halved to 0.5 so it doesn't cancel the swing.
- **Torso balance:**
  - The P gain rises to 6 and the D gain to 0.8.
  - The forward-lean bias rises to 0.3, which targets about 0.05 rad of forward lean, to counter the backward drift.
  - The speed feedback rises to −0.15·obs[5].

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.3, "a1": -0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -6.0, "obs[7]": -0.8, "obs[5]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_posture", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_posture", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "push_thrust", "inputs": {"sin(hop)": 1.0}, "threshold": 0.0,
    "sharpness": 3.0, "to": {"a1": 0.7, "a2": 0.3}},
   {"type": "linear", "name": "swing_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a0": 0.35}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | 0.03 | 0.38 | torso angle out of range
1 | 0.03 | 0.37 | torso angle out of range
2 | 0.03 | 0.38 | torso angle out of range
3 | 0.03 | 0.38 | torso angle out of range
4 | 0.03 | 0.38 | torso angle out of range
5 | 0.02 | 0.38 | torso angle out of range
6 | 0.03 | 0.38 | torso angle out of range
7 | 0.02 | 0.38 | torso angle out of range
8 | 0.03 | 0.37 | torso angle out of range
9 | 0.03 | 0.38 | torso angle out of range

Over the 10 episodes: mean d 0.03 m, min 0.02, max 0.03; mean time survived 0.37 s; mean forward speed 0.07 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.063 | 0.017 | 0.40 | 0.23
leg | -0.449 | 0.003 | 0.38 | 0.00
foot | -0.052 | 0.084 | 0.17 | 0.00
torso angle min -0.195, max 0.013 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.79 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.01 | 1.21 | 0.008 | yes | 1.63
0.20 | 0.05 | 1.21 | 0.007 | yes | 3.14
0.30 | 0.06 | 1.23 | -0.048 | yes | 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance: 0.00
thigh_posture: 0.00
leg_posture: 0.00
foot_posture: 0.00
swing_rhythm: 0.00

## Now: round 2 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
