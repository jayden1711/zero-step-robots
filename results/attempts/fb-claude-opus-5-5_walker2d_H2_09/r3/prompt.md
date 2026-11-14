# Task: design the controller network of a simulated walking robot

You will design the controller of a simulated robot. You cannot run code yourself. After each design you write, we
test it on 10 practice episodes and send you a fixed summary of the results; you then revise it. There are 6 designs in
total: this first one (round 0) and 5 revisions (rounds 1 to 5). Your round-5 design is final and is scored exactly as
written, on different episodes from the practice ones. There is no training: the numbers you write become the final
weights of the controller network.

## The robot and environment

Environment: Gymnasium `Walker2d-v5` (MuJoCo), a planar two-legged robot (torso; right and left thigh, leg and
foot) that moves in the x-z plane. Forward is +x.

- Observation `obs` (17 numbers, raw, not normalised; indices from 0):
  - obs[0]: height (z) of the torso
  - obs[1]: torso angle (radians)
  - obs[2]: right thigh joint angle
  - obs[3]: right leg joint angle
  - obs[4]: right foot joint angle
  - obs[5]: left thigh joint angle
  - obs[6]: left leg joint angle
  - obs[7]: left foot joint angle
  - obs[8]: torso x-velocity
  - obs[9]: torso z-velocity
  - obs[10]: torso angular velocity
  - obs[11] to obs[16]: angular velocities of the six joints, in the same order as obs[2] to obs[7]

  Velocities (obs[8] to obs[16]) are clipped to [-10, 10].
- Action (6 numbers): the torques at the right thigh, right leg, right foot, left thigh, left leg and left foot
  joints, in that order (a0 to a5). Values outside [-1, 1] are clipped to that range.
- One step is 0.008 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.005).

Episode rules:

- The walker is healthy while both hold: 0.8 < torso height z < 2.0, and -1 < torso angle < 1 (radians).
- The episode terminates as soon as the walker is not healthy. Otherwise it is cut off after 1000 steps.
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

A workable structure for this robot is a walking gait with the two legs in antiphase:

- Two oscillators, one per leg, coupled so that they settle half a cycle (pi radians) apart. Each leg alternates
  stance (on the ground, pushing the body forward, thigh swinging back) and swing (knee flexed to clear the ground,
  thigh swinging forward). The phase relationship between a leg's joints is fixed by how each joint's command is
  taken from that leg's oscillator's cos and sin outputs.
- Balance feedback is added on top of the rhythm: the torso angle (obs[1]) and the torso angular velocity
  (obs[10]) feed back to the thigh joints so the torso stays upright, and forward speed is regulated through how far
  the torso leans.

Facts and ranges (from the model files and the documentation, not tuned for you):

- Sign conventions. A positive torso angle (obs[1]) means the torso leans forward (towards +x). For every thigh,
  leg and foot joint, a positive torque drives the joint angle up, and a negative joint angle swings the part below
  the joint backwards (towards -x). Thigh and leg joint angles are limited to [-2.62, 0] radians (0 = straight in
  line with the part above), the feet to [-0.79, 0.79].
- With a foot on the ground, a negative torque at that leg's thigh pitches the torso backward (the reaction at
  the hip).
- Admissible ranges: oscillator frequency 0.5 to 2 Hz for the stride of a robot this size; rhythmic torque
  amplitude up to 1 (the action limit) per joint; feedback that holds the torso upright opposes the sign of
  obs[1] and of obs[10] at the stance-leg thigh.

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
16), `cos(NAME)` or `sin(NAME)` for an oscillator called NAME. Actions are named `a0` to a5.

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

    {"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
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

Round-0 design: an antiphase CPG with PD-style joint tracking. Balance is handled by torso feedback at both hips, a gated knee flexion during swing, and compliant ankles. This round is partly a probe; the results will tell me what to tune.

- **Rhythm:** oscillators R and L run at 0.9 Hz, held π apart by symmetric coupling.
  - They start at +π/2 and −π/2, so one leg begins at the end of swing (thigh near 0, under the hip) and the other at the end of stance.
- **Thighs (a0, a3):** each is one linear unit that combines four terms:
  - **Joint stiffness:** Kp = 2 toward the target q* = −0.3 + 0.25·sin φ. The thigh angle rises during swing, when cos φ > 0, and falls during stance.
  - **Leg damping in the world frame:** −0.3·(q̇_thigh − obs[10]). This damps the swinging leg without adding much damping to the light torso.
  - **Torso feedback:** −1.0·obs[1] − 0.11·obs[10].
  - **Bias:** the target offset plus a torso lean target of −0.15 rad (slightly back), so feet can land a little ahead of the hip given the thigh range [−2.62, 0].
- **Knees (a1, a4):**
  - A PD unit holds each knee nearly straight (target −0.05).
  - A reflex unit adds about −1.2 of flexion torque in a phase window centred slightly before mid-swing, using cos(φ+0.4) > 0.3. The bias is set so the net flexion torque is zero in stance.
- **Feet (a2, a5):** soft PD toward 0.

The gains are kept small enough to stay stable with the 0.008 s zero-order hold, given the torso's small inertia (about 0.2 kg·m²).

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.5708}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.1416},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.1416}
 ],
 "bias": {"a0": -0.75, "a3": -0.75, "a1": -0.7, "a4": -0.7},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[2]": -2.0, "obs[11]": -0.3, "obs[10]": 0.19, "obs[1]": -1.0, "sin(R)": 0.5},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[5]": -2.0, "obs[14]": -0.3, "obs[10]": 0.19, "obs[1]": -1.0, "sin(L)": 0.5},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -2.0, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -2.0, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.6}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.6}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.97 | 1.37 | torso angle out of range
1 | -1.04 | 1.40 | torso angle out of range
2 | -0.91 | 1.55 | torso angle out of range
3 | -0.83 | 1.42 | torso angle out of range
4 | -0.83 | 1.43 | torso angle out of range
5 | -0.85 | 1.52 | torso angle out of range
6 | -0.97 | 1.45 | torso angle out of range
7 | -0.88 | 1.54 | torso angle out of range
8 | -0.96 | 1.39 | torso angle out of range
9 | -0.96 | 1.45 | torso angle out of range

Over the 10 episodes: mean d -0.92 m, min -1.04, max -0.83; mean time survived 1.45 s; mean forward speed -0.64 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.515 | 0.022 | 0.88 | 0.68
right leg | -0.637 | 0.003 | 0.68 | 0.02
right foot | -0.109 | 0.125 | 0.07 | 0.00
left thigh | -0.532 | 0.020 | 0.91 | 0.75
left leg | -0.731 | 0.002 | 0.64 | 0.02
left foot | -0.128 | 0.217 | 0.07 | 0.00
torso angle min -0.996, max -0.005 rad; torso height min 0.92, max 1.25 m
right foot: on the ground 0.54 of the steps, 18 touchdowns
left foot: on the ground 0.68 of the steps, 16 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.08 | 1.17 | -0.548 | yes | no | 2.16, 5.30
0.20 | -0.08 | 1.19 | -0.393 | no | yes | 2.70, 5.84
0.30 | -0.10 | 1.20 | -0.341 | yes | no | 3.29, 0.15
0.40 | -0.14 | 1.18 | -0.540 | yes | yes | 3.83, 0.69
0.50 | -0.15 | 1.19 | -0.346 | yes | yes | 4.42, 1.28
0.60 | -0.20 | 1.19 | -0.414 | yes | yes | 4.96, 1.82
0.70 | -0.27 | 1.17 | -0.607 | no | yes | 5.55, 2.41
0.80 | -0.31 | 1.17 | -0.487 | no | yes | 6.09, 2.95
0.90 | -0.40 | 1.13 | -0.756 | no | yes | 0.40, 3.54
1.00 | -0.49 | 1.10 | -0.791 | yes | yes | 0.94, 4.08
1.10 | -0.57 | 1.14 | -0.457 | no | no | 1.53, 4.67
1.20 | -0.72 | 1.07 | -0.821 | yes | no | 2.07, 5.22
1.30 | -0.88 | 0.98 | -0.937 | no | yes | 2.66, 5.80

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thigh_R: 0.13
thigh_L: 0.08
knee_R: 0.00
knee_L: 0.00
foot_R: 0.00
foot_L: 0.00

## Round 1: your reply

## Round 1 design

### What went wrong in round 0

All 10 runs fell the same way. The torso pitched backward within 0.1 s, to −0.55 rad, and the robot then drifted backward until the torso angle passed −1.

The cause is the thigh control. Both thighs had a constant bias of −0.75, and they were held stiffly toward a *joint* angle of −0.3. With the feet on the ground, driving the joint angle negative rotates the torso backward instead of moving the leg. That joint stiffness (gain 2) was larger than the torso feedback (gain 1), so it won. The thighs were also saturated about 70% of the time.

### Changes in round 1

- **Thigh PD now targets the leg's angle in the world frame, not the joint angle.**
  - The leg's forward angle in the world is φ_w = q_thigh − obs[1].
  - The PD term is Kp·(φ* − q + obs[1]) − Kd·(q̇ − obs[10]).
  - With the foot planted, this term no longer moves the torso, so torso control and leg tracking stay separate.
- **Torso PD now dominates the thigh command.**
  - The term is −3·(obs[1] − lean) − 0.12·obs[10] at each thigh.
  - The damping is chosen to stay well inside the stability limit for the 0.008 s step.
- **The lean target is −0.2 rad (slightly back).**
  - Thigh angles must stay ≤ 0, so a backward lean is the only way the swing foot can land ahead of the hip.
  - The constant thigh bias is now only the lean term (−0.6). It is cancelled once the torso reaches its target.
- **The rhythm amplitude is ±0.25 rad around a vertical leg.** The two legs are in antiphase, so their torques largely cancel on the torso.
- **Knees, feet and oscillators are unchanged.**

### The thigh unit, term by term

| Input | Coefficient | Source |
|---|---|---|
| obs[1] (torso angle) | −1.5 | Kp − Kt = 1.5 − 3 |
| thigh angle | −1.5 | −Kp |
| torso angular velocity | +0.08 | Kd − Kdt = 0.2 − 0.12 |
| thigh velocity | −0.2 | −Kd |
| sin(phase) | 0.375 | Kp · 0.25 |
| bias | −0.6 | Kt · lean = 3 · (−0.2) |

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.5708}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.1416},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.1416}
 ],
 "bias": {"a0": -0.6, "a3": -0.6, "a1": -0.7, "a4": -0.7},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[1]": -1.5, "obs[2]": -1.5, "obs[10]": 0.08, "obs[11]": -0.2, "sin(R)": 0.375},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[1]": -1.5, "obs[5]": -1.5, "obs[10]": 0.08, "obs[14]": -0.2, "sin(L)": 0.375},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -2.0, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -2.0, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.6}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.6}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.20 | 1.69 | height too low
1 | -1.23 | 1.69 | height too low
2 | -1.25 | 1.75 | height too low
3 | -1.20 | 1.70 | height too low
4 | -1.24 | 1.76 | height too low
5 | -1.24 | 1.78 | height too low
6 | -1.17 | 1.64 | height too low
7 | -1.21 | 1.78 | height too low
8 | -1.22 | 1.66 | height too low
9 | -1.06 | 1.54 | torso angle out of range

Over the 10 episodes: mean d -1.20 m, min -1.25, max -1.06; mean time survived 1.70 s; mean forward speed -0.71 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.417 | 0.025 | 0.83 | 0.54
right leg | -0.633 | 0.003 | 0.63 | 0.01
right foot | -0.129 | 0.096 | 0.06 | 0.00
left thigh | -0.361 | 0.026 | 0.94 | 0.70
left leg | -0.708 | 0.002 | 0.59 | 0.02
left foot | -0.226 | 0.198 | 0.07 | 0.00
torso angle min -0.961, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.50 of the steps, 16 touchdowns
left foot: on the ground 0.72 of the steps, 15 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.06 | 1.19 | -0.403 | yes | yes | 2.16, 5.30
0.20 | -0.07 | 1.20 | -0.283 | no | no | 2.70, 5.84
0.30 | -0.10 | 1.19 | -0.461 | yes | yes | 3.29, 0.15
0.40 | -0.13 | 1.19 | -0.430 | yes | yes | 3.83, 0.69
0.50 | -0.13 | 1.20 | -0.246 | yes | yes | 4.42, 1.28
0.60 | -0.18 | 1.20 | -0.348 | yes | yes | 4.96, 1.82
0.70 | -0.23 | 1.19 | -0.415 | no | yes | 5.55, 2.41
0.80 | -0.26 | 1.18 | -0.435 | no | yes | 6.09, 2.95
0.90 | -0.31 | 1.17 | -0.549 | no | yes | 0.40, 3.54
1.00 | -0.35 | 1.17 | -0.432 | no | yes | 0.94, 4.08
1.10 | -0.40 | 1.17 | -0.332 | yes | no | 1.53, 4.67
1.20 | -0.50 | 1.15 | -0.532 | yes | no | 2.07, 5.22
1.30 | -0.60 | 1.11 | -0.569 | yes | no | 2.66, 5.80
1.40 | -0.73 | 1.05 | -0.716 | no | yes | 3.20, 0.06

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thigh_R: 0.00
thigh_L: 0.00
knee_R: 0.00
knee_L: 0.00
foot_R: 0.00
foot_L: 0.00

## Round 2: your reply

## Round 2 design

### What went wrong in round 1

The torso still settled about 0.4 rad backward, and the robot again walked backward until it fell.

The cause was in how the thigh gains combined:

- The world-frame leg term added +Kp·obs[1] to each thigh command. That cancelled half of the torso stiffness, leaving a net gain of only −1.5.
- The constant lean bias of −0.6 then set the equilibrium at about −0.6 / 1.5 = −0.4 rad. That matches the measured lean.
- Leaning that far back puts the centre of mass behind the feet. The robot therefore drifted backward.
- The deep crouch at the end (height too low) came from the knees giving way while leaning back.

### Changes in round 2

- **Torso stiffness now dominates.**
  - Kt = 3 and Kp = 1, so the net obs[1] gain at each thigh is −2.
  - Torso damping is Kdt = 0.1 and leg damping Kd = 0.15, so the obs[10] coefficient is +0.05.
- **The lean target is almost upright (−0.05 rad).**
  - The leg target is now φ_w* = −0.1 + 0.3·sin φ in the world frame, so each leg is slightly behind the hip on average.
  - The bias is Kt·lean + Kp·φ0 = −0.15 − 0.1 = −0.25, much smaller than before.
- **Speed feedback is added: −0.15·obs[8] at each thigh.**
  - When the robot moves backward, the torso is commanded to lean forward, and the reverse when it moves forward.
  - This acts as lean = l0 − 0.05·v.
- **The knees are stiffer.**
  - The PD gain is 3, the damping 0.15, and the bias is −0.65.
  - With these values the stance knee holds near straight, with a net offset of about −0.05.
  - The swing flexion is a little stronger, at −0.7.
- **Oscillators and feet are unchanged.**

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.5708}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.1416},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.1416}
 ],
 "bias": {"a0": -0.25, "a3": -0.25, "a1": -0.65, "a4": -0.65},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[1]": -2.0, "obs[2]": -1.0, "obs[10]": 0.05, "obs[11]": -0.15, "obs[8]": -0.15, "sin(R)": 0.3},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[1]": -2.0, "obs[5]": -1.0, "obs[10]": 0.05, "obs[14]": -0.15, "obs[8]": -0.15, "sin(L)": 0.3},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -3.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -3.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.7}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.7}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.03 | 1.42 | torso angle out of range
1 | -1.07 | 1.45 | torso angle out of range
2 | -1.00 | 1.41 | torso angle out of range
3 | -1.04 | 1.43 | torso angle out of range
4 | -1.03 | 1.45 | torso angle out of range
5 | -1.00 | 1.34 | height too low
6 | -1.02 | 1.34 | height too low
7 | -1.03 | 1.42 | torso angle out of range
8 | -1.03 | 1.34 | height too low
9 | -1.03 | 1.41 | torso angle out of range

Over the 10 episodes: mean d -1.03 m, min -1.07, max -1.00; mean time survived 1.40 s; mean forward speed -0.74 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.120 | 0.028 | 0.82 | 0.48
right leg | -0.406 | 0.011 | 0.54 | 0.25
right foot | -0.159 | 0.108 | 0.06 | 0.00
left thigh | -0.108 | 0.038 | 0.69 | 0.38
left leg | -0.466 | 0.016 | 0.53 | 0.18
left foot | -0.138 | 0.203 | 0.06 | 0.00
torso angle min -0.987, max -0.005 rad; torso height min 0.83, max 1.25 m
right foot: on the ground 0.60 of the steps, 10 touchdowns
left foot: on the ground 0.71 of the steps, 15 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.03 | 1.20 | -0.158 | yes | no | 2.16, 5.30
0.20 | -0.05 | 1.21 | -0.178 | no | no | 2.70, 5.84
0.30 | -0.08 | 1.20 | -0.191 | yes | no | 3.29, 0.15
0.40 | -0.12 | 1.20 | -0.222 | yes | no | 3.83, 0.69
0.50 | -0.15 | 1.20 | -0.142 | no | yes | 4.42, 1.28
0.60 | -0.20 | 1.20 | -0.218 | yes | yes | 4.96, 1.82
0.70 | -0.25 | 1.19 | -0.248 | no | yes | 5.55, 2.41
0.80 | -0.31 | 1.18 | -0.262 | yes | yes | 6.09, 2.95
0.90 | -0.40 | 1.16 | -0.350 | yes | yes | 0.40, 3.54
1.00 | -0.48 | 1.15 | -0.399 | yes | no | 0.94, 4.08
1.10 | -0.56 | 1.14 | -0.385 | yes | no | 1.53, 4.67
1.20 | -0.68 | 1.10 | -0.496 | no | yes | 2.07, 5.22
1.30 | -0.84 | 1.00 | -0.711 | no | yes | 2.66, 5.80
1.40 | -1.01 | 0.85 | -0.966 | no | yes | 3.20, 0.06

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
thigh_R: 0.00
thigh_L: 0.00
knee_R: 0.00
knee_L: 0.00
foot_R: 0.00
foot_L: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
