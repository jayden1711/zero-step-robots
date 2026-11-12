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

This first design uses PD tracking of a rhythmic gait, with torso balance and a small speed correction added on top. Two oscillators are locked half a cycle apart. One choice matters most, and the round-0 results should test it.

**Sign assumption.** Walker2d's root pitch joint (`rooty`) turns about the same axis as every leg joint, `0 -1 0`. With that axis, a positive thigh torque applies the opposite torque to the torso, so it drives obs[1] *down*. The brief states that a positive obs[1] means a forward lean. The joint axes imply the opposite: positive obs[1] tilts the top of the torso towards −x. I followed the axis algebra:
- Upright feedback is `+K·obs[1]` and `+K·obs[10]` at the hips.
- The world angle of each leg is `obs[1] + thigh angle`.

This differs from the hint's "opposes the sign of obs[1]". If the torso goes over within the first few dozen steps, flipping this sign is the first thing I'll change.

**Gait (0.8 Hz):**
- **Thighs:** each thigh tracks a target angle measured relative to the world: −0.05 + 0.22·cos φ. The foot lands at about +0.17 rad (ahead of the hip) and pushes back to −0.27 rad.
- **Torso lean:** the thigh joint cannot go above 0 (in front of the torso line). The torso is therefore held at obs[1] ≈ 0.2, which by the axis convention above is a slight backward lean. This lets the feet land ahead of the hip without pressing into that limit.
- **Knees:** each knee tracks −0.3 + 0.5·sin(φ + 0.63). It is straight from foot strike through mid-stance, bends up to 0.8 rad early in the swing, and straightens again before the next strike.
- **Speed correction:** the hip targets shift with (obs[8] − 0.6) to rein in speed. A positive shift brakes through the stance leg.
- **Ankles:** a soft PD controller holds each ankle near 0.
- **Startup phases:** the right leg starts at mid-stance and the left at mid-swing.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.365, "a1": -0.6, "a3": -0.365, "a4": -0.6},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.33, "obs[1]": -0.5, "obs[2]": -1.5, "obs[10]": -0.03, "obs[11]": -0.15, "obs[8]": 0.15},
    "range": 2.0, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.8, "cos(R)": 0.58, "obs[3]": -2.0, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.4, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.33, "obs[1]": -0.5, "obs[5]": -1.5, "obs[10]": -0.03, "obs[14]": -0.15, "obs[8]": 0.15},
    "range": 2.0, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.8, "cos(L)": 0.58, "obs[6]": -2.0, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.4, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

Each hip unit combines three terms:
- leg-angle PD tracking: Kp = 1.5 and Kd = 0.15 (in action units, 1 = 100 N·m)
- torso feedback: Kb = 1.0 on (obs[1] − 0.2) and Kbd = 0.12 on obs[10]
- the speed term on obs[8]

The constant parts of the targets are moved into `bias`, because linear units have no constant input. Ten of the 16 hidden units are still free for later rounds, for example phase-gated stance/swing reflexes or oscillator phase feedback.

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.21 | 3.01 | torso angle out of range
1 | -1.17 | 2.36 | torso angle out of range
2 | -0.84 | 2.64 | torso angle out of range
3 | -0.97 | 3.20 | torso angle out of range
4 | -1.10 | 2.43 | torso angle out of range
5 | -1.10 | 3.05 | torso angle out of range
6 | -0.87 | 2.61 | torso angle out of range
7 | -1.04 | 2.53 | torso angle out of range
8 | -0.83 | 2.61 | torso angle out of range
9 | -1.18 | 2.42 | torso angle out of range

Over the 10 episodes: mean d -1.03 m, min -1.21, max -0.83; mean time survived 2.69 s; mean forward speed -0.39 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.502 | 0.011 | 0.94 | 0.74
right leg | -0.758 | 0.013 | 0.60 | 0.00
right foot | -0.147 | 0.199 | 0.04 | 0.00
left thigh | -0.494 | 0.003 | 0.93 | 0.70
left leg | -0.731 | 0.014 | 0.59 | 0.00
left foot | -0.176 | 0.223 | 0.05 | 0.00
torso angle min -0.995, max -0.005 rad; torso height min 0.90, max 1.25 m
right foot: on the ground 0.61 of the steps, 47 touchdowns
left foot: on the ground 0.65 of the steps, 43 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.05 | 1.19 | -0.313 | yes | yes | 2.09, 5.24
0.20 | -0.08 | 1.18 | -0.505 | no | yes | 2.58, 5.72
0.30 | -0.10 | 1.17 | -0.509 | no | yes | 3.10, 6.24
0.40 | -0.11 | 1.19 | -0.413 | yes | yes | 3.58, 0.44
0.50 | -0.11 | 1.20 | -0.378 | no | no | 4.10, 0.96
0.60 | -0.11 | 1.20 | -0.368 | yes | yes | 4.59, 1.45
0.70 | -0.12 | 1.19 | -0.460 | yes | yes | 5.11, 1.97
0.80 | -0.13 | 1.18 | -0.516 | no | yes | 5.59, 2.45
0.90 | -0.15 | 1.17 | -0.518 | yes | yes | 6.11, 2.97
1.00 | -0.16 | 1.19 | -0.444 | yes | no | 0.31, 3.46
1.10 | -0.17 | 1.19 | -0.403 | yes | yes | 0.84, 3.98
1.20 | -0.17 | 1.19 | -0.387 | yes | no | 1.32, 4.46
1.30 | -0.18 | 1.19 | -0.458 | yes | no | 1.84, 4.98
1.40 | -0.20 | 1.18 | -0.544 | yes | yes | 2.32, 5.47

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
hip_R: 0.31
knee_R: 0.00
ankle_R: 0.00
hip_L: 0.36
knee_L: 0.00
ankle_L: 0.00

## Round 1: your reply

# Round 1: switching to the brief's sign convention for torso balance

**What round 0 showed.** In the first 0.1 s the torso swung to about −0.3 and then stayed near −0.45 while the robot drifted backwards at −0.4 m/s. That fits the brief's convention, where negative obs[1] means a backward lean and a negative thigh torque pitches the torso back. It does not fit my joint-axis reading. The hips also saturated for about 70% of steps because the large negative bias kept pressing the thighs back.

**Changes in this design:**
1. **Balance sign.** I now use the brief's convention. The hip balance term is −Kb·(obs[1] − θ₀) − Kbd·obs[10], with Kb = 1.5 and Kbd = 0.15. The leg's forward angle relative to vertical is taken as obs[2] − obs[1]. With that reading, round 0's −0.45 lean plus thighs near −0.25 put the feet ahead of the hip while leaning back, which explains the backward drift.
2. **Hip tracking in joint space.** Each thigh tracks −0.225 + 0.225·cos φ, so it stays inside the joint limit (between −0.45 and 0). Kp is lowered to 1.0 and Kd is 0.1. The constant bias is smaller (−0.19 instead of −0.365), and the declared range is wider so the unit saturates less.
3. **Lean target and speed control.** The lean target is θ₀ = 0.025 − 0.15·obs[8], about −0.05 at 0.5 m/s. A slight backward lean lets the swing foot land in front of the hip. Going faster gives a negative hip torque, which pitches the torso back and slows the robot.
4. **Knee timing.** Each knee tracks −0.3 + 0.5·sin(φ + 0.4), with Kp = 1.5. The knee is straight through stance and flexes most early in the swing.
5. **Frequency.** Raised from 0.8 Hz to 1.0 Hz.
6. **Ankles.** Slightly stiffer.

**What to test.** If the torso now falls forward and the robot runs off, the lean offset is the next thing to tune. If the torso still drifts negative, the hip bias is.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.19, "a1": -0.45, "a3": -0.19, "a4": -0.45},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.225, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -1.5, "obs[10]": -0.15, "obs[8]": -0.225},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.69, "cos(R)": 0.29, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.225, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -1.5, "obs[10]": -0.15, "obs[8]": -0.225},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.69, "cos(L)": 0.29, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.06 | 1.34 | torso angle out of range
1 | -1.10 | 1.31 | torso angle out of range
2 | -1.13 | 1.40 | torso angle out of range
3 | -1.08 | 1.35 | torso angle out of range
4 | -1.11 | 1.38 | torso angle out of range
5 | -1.08 | 1.35 | torso angle out of range
6 | -1.07 | 1.33 | torso angle out of range
7 | -1.07 | 1.35 | torso angle out of range
8 | -1.10 | 1.32 | torso angle out of range
9 | -1.08 | 1.34 | torso angle out of range

Over the 10 episodes: mean d -1.09 m, min -1.13, max -1.06; mean time survived 1.35 s; mean forward speed -0.81 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.159 | 0.030 | 0.60 | 0.31
right leg | -0.576 | 0.003 | 0.31 | 0.00
right foot | -0.166 | 0.208 | 0.05 | 0.00
left thigh | -0.055 | 0.049 | 0.55 | 0.13
left leg | -0.596 | 0.002 | 0.30 | 0.00
left foot | -0.130 | 0.190 | 0.05 | 0.00
torso angle min -0.980, max -0.005 rad; torso height min 0.86, max 1.25 m
right foot: on the ground 0.68 of the steps, 8 touchdowns
left foot: on the ground 0.75 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.03 | 1.20 | -0.139 | yes | yes | 0.65, 3.80
0.20 | -0.06 | 1.20 | -0.219 | yes | no | 1.26, 4.40
0.30 | -0.10 | 1.20 | -0.261 | yes | yes | 1.91, 5.05
0.40 | -0.13 | 1.19 | -0.261 | yes | yes | 2.51, 5.65
0.50 | -0.19 | 1.18 | -0.281 | yes | yes | 3.17, 0.03
0.60 | -0.26 | 1.17 | -0.344 | no | yes | 3.77, 0.63
0.70 | -0.31 | 1.18 | -0.328 | yes | yes | 4.42, 1.28
0.80 | -0.39 | 1.16 | -0.323 | yes | yes | 5.03, 1.88
0.90 | -0.51 | 1.13 | -0.444 | yes | no | 5.68, 2.54
1.00 | -0.61 | 1.11 | -0.529 | yes | no | 0.00, 3.14
1.10 | -0.71 | 1.11 | -0.525 | yes | yes | 0.65, 3.80
1.20 | -0.84 | 1.05 | -0.630 | no | yes | 1.26, 4.40
1.30 | -1.02 | 0.91 | -0.901 | no | yes | 1.91, 5.05

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
hip_R: 0.00
knee_R: 0.00
ankle_R: 0.00
hip_L: 0.00
knee_L: 0.00
ankle_L: 0.00

## Round 2: your reply

# Round 2: keep the hips off their joint limit

## What round 1 showed

- **The balance sign was right.** In both rounds the torso leaned to negative angles and the robot moved backwards. The final fall in round 1 was backwards, with x dropping faster and faster. So a negative obs[1] means a backward lean, as the brief says. A negative hip torque also pitched the torso back.
- **The hips were pinned at their limit.** In round 1 both thighs stayed between about −0.16 and +0.05. That is at the 0 limit (the leg in line with the torso), with 31% of hip actions saturated. The balance term and the speed term pushed the thighs up into that limit. At the limit, hip torque cannot rotate the torso. The robot then became a rigid stick and tipped backwards.
- **The stick has its feet in front.** The leg's angle from vertical (forward positive) is about thigh angle − obs[1]. The thighs can only move backwards from the torso line. So the only way to put a foot ahead of the hip is a slight backward torso lean, with the thigh kept below 0. Round 0 settled at a torso angle of −0.45 with the feet mostly ahead, which explains its backward stepping. The fix is a small backward lean with the thighs well clear of 0.

## Design for round 2

1. **Hip target in joint space:** −0.35 + 0.25·cos φ, a range of −0.6 to −0.1.
   - The thigh never asks to reach 0, so the stance hip always has room to correct the torso.
   - With the torso at about −0.25, the leg angle from vertical runs from +0.15 at foot strike to −0.35 at push-off.
   - On average the feet are slightly behind the hip, so the robot tends to fall forward.
   - Kp = 1.0 and Kd = 0.1.
2. **Torso balance:** −1.0·(obs[1] + 0.25) − 0.1·obs[10].
   - The speed term is −0.15·(obs[8] − 0.6). It leans the torso further back when the robot goes too fast and forward when it goes too slow or backwards.
   - The constant part goes into the bias: a0 = a3 = −0.51.
   - With the stance foot planted, a backward torso tilt also lowers the thigh angle, so the joint PD term and the balance term both push the same way.
3. **Knee target:** −0.25 + 0.55·sin(φ + 0.4).
   - Stance runs from φ = 0 (foot strike, thigh most forward) to π. The knee is straight there, held by the 0 limit.
   - The knee starts to flex just before push-off. It is most flexed (−0.8) in mid-swing and almost straight at the next strike.
4. **Starting phases are symmetric** (π/2 and 3π/2). Both thigh targets start equal, so the opening transient pitches the torso less. The right leg starts at mid-stance and the left at mid-swing with its knee flexed.
5. **Frequency is 0.8 Hz.** That should give roughly 0.6 to 0.8 m/s.

**What to test.** If the torso now falls forward, the next change is a smaller lean offset or a less negative hip centre. If it still drifts backwards past −0.4, the next change is a higher Kb.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.51, "a1": -0.375, "a3": -0.51, "a4": -0.375},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.25, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -1.0, "obs[10]": -0.1, "obs[8]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.76, "cos(R)": 0.32, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.25, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -1.0, "obs[10]": -0.1, "obs[8]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.76, "cos(L)": 0.32, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.10 | 2.11 | torso angle out of range
1 | -1.22 | 2.34 | height too low
2 | -1.26 | 2.34 | height too low
3 | -1.22 | 2.30 | height too low
4 | -1.27 | 2.34 | height too low
5 | -1.21 | 2.34 | height too low
6 | -1.24 | 2.35 | height too low
7 | -1.18 | 2.52 | torso angle out of range
8 | -1.13 | 2.58 | torso angle out of range
9 | -1.25 | 2.34 | height too low

Over the 10 episodes: mean d -1.21 m, min -1.27, max -1.10; mean time survived 2.36 s; mean forward speed -0.51 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.445 | 0.029 | 0.87 | 0.66
right leg | -0.719 | 0.023 | 0.42 | 0.00
right foot | -0.137 | 0.132 | 0.05 | 0.00
left thigh | -0.508 | 0.024 | 0.88 | 0.58
left leg | -0.722 | 0.026 | 0.44 | 0.00
left foot | -0.152 | 0.184 | 0.06 | 0.00
torso angle min -0.992, max -0.005 rad; torso height min 0.86, max 1.25 m
right foot: on the ground 0.64 of the steps, 27 touchdowns
left foot: on the ground 0.66 of the steps, 16 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.06 | 1.19 | -0.352 | yes | yes | 2.09, 5.24
0.20 | -0.07 | 1.19 | -0.461 | no | yes | 2.58, 5.72
0.30 | -0.09 | 1.18 | -0.480 | yes | yes | 3.10, 6.24
0.40 | -0.12 | 1.19 | -0.461 | yes | no | 3.58, 0.44
0.50 | -0.14 | 1.19 | -0.427 | no | yes | 4.10, 0.96
0.60 | -0.15 | 1.19 | -0.427 | no | yes | 4.59, 1.45
0.70 | -0.16 | 1.19 | -0.482 | yes | yes | 5.11, 1.97
0.80 | -0.17 | 1.18 | -0.530 | yes | yes | 5.59, 2.45
0.90 | -0.18 | 1.18 | -0.525 | yes | yes | 6.11, 2.97
1.00 | -0.21 | 1.18 | -0.523 | yes | no | 0.31, 3.46
1.10 | -0.24 | 1.18 | -0.472 | yes | no | 0.84, 3.98
1.20 | -0.27 | 1.18 | -0.479 | yes | no | 1.32, 4.46
1.30 | -0.31 | 1.17 | -0.515 | yes | no | 1.84, 4.98
1.40 | -0.35 | 1.16 | -0.555 | yes | yes | 2.32, 5.47

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
hip_R: 0.09
knee_R: 0.00
ankle_R: 0.00
hip_L: 0.16
knee_L: 0.00
ankle_L: 0.00

## Round 3: your reply

# Round 3: reverse the torso-balance sign, based on what the robot actually did

## What rounds 0 to 2 show

- **Which way is a backward lean.** In every run the torso angle went negative while x decreased, and decreased faster as the angle grew. The robot fell backwards each time. So a negative obs[1] is a backward lean, as the brief says.
- **The balance feedback had the wrong sign in all three rounds.** The net gain from obs[1] to the hips was negative every time: −0.5, −1.5 and −1.0. The hip joint and the torso share one axis, so a hip torque pushes the torso the opposite way. A positive thigh torque therefore pitches the torso to a more negative angle, which is backwards.
  - With a negative gain, a backward lean produced a positive torque.
  - That torque pinned the stance thigh at its 0 limit, which is why the thighs sat near 0 for 30–70% of steps.
  - The reaction then tipped the torso further back, so the feedback made the backward fall worse.
  - The brief's claim that "a negative thigh torque pitches the torso backward" is the opposite of what the data shows.
- **Which way a negative thigh angle moves the foot.** The same shared-axis rule means a negative thigh angle swings the foot forward. That also explains round 2. It held the thighs near −0.35 with the torso at −0.5, which put the feet far ahead and made the robot walk backwards.

## Design for round 3

1. **Balance: +1.0·(obs[1] − θₜ) + 0.1·obs[10] at both hips.** A backward lean now produces a negative hip torque, which pitches the torso forward.
   - With the foot planted, the hip PD on the thigh angle also stabilises the torso.
   - Both terms now act in the same direction.
2. **Forward lean target.** θₜ = 0.3 − 0.1·obs[8], so about 0.25 rad of forward lean at walking speed.
   - Thighs can only bend forward from the torso line, so a forward lean is the only way to get the stance foot behind the hip at push-off.
   - When the robot goes faster, θₜ drops and the torso is brought back, which slows it down.
3. **Thigh target: −0.25 − 0.22·cos φ.**
   - At φ = 0 (foot strike) it is −0.47, foot forward.
   - At φ = π (push-off) it is −0.03.
   - With the torso at 0.25, the stance leg sweeps from about +0.22 rad ahead of vertical to −0.22 behind.
   - Kp = 1.0, Kd = 0.1. Bias = −0.25 − 0.30 = −0.55.
4. **Knee target: −0.05 + 0.65·sin(φ + 0.3).**
   - The knee is held straight (against its limit) through stance.
   - It starts flexing just before push-off, reaches −0.7 in mid-swing, and is straight again before the next strike.
5. **Frequency 0.9 Hz, symmetric start.** The oscillators start at π/2 and 3π/2, so both thigh targets are equal at t = 0. The right leg starts in stance and the left in swing.

**What to check next round:** if the torso now falls forward (angle above +1), the fix is to reduce the lean offset in the bias, not to flip the sign again.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.55, "a1": -0.075, "a3": -0.55, "a4": -0.075},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": -0.22, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": 1.0, "obs[10]": 0.1, "obs[8]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.93, "cos(R)": 0.29, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": -0.22, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": 1.0, "obs[10]": 0.1, "obs[8]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.93, "cos(L)": 0.29, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.07 | 0.06 | torso angle out of range
1 | -0.07 | 0.06 | torso angle out of range
2 | -0.07 | 0.06 | torso angle out of range
3 | -0.07 | 0.06 | torso angle out of range
4 | -0.07 | 0.06 | torso angle out of range
5 | -0.07 | 0.06 | torso angle out of range
6 | -0.07 | 0.06 | torso angle out of range
7 | -0.07 | 0.06 | torso angle out of range
8 | -0.07 | 0.06 | torso angle out of range
9 | -0.07 | 0.06 | torso angle out of range

Over the 10 episodes: mean d -0.07 m, min -0.07, max -0.07; mean time survived 0.06 s; mean forward speed -1.32 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.965 | -0.005 | 0.62 | 0.00
right leg | 0.003 | 0.017 | 0.76 | 0.00
right foot | -0.008 | 0.015 | 0.03 | 0.00
left thigh | -0.890 | 0.001 | 0.74 | 0.00
left leg | -0.142 | 0.002 | 0.56 | 0.14
left foot | 0.000 | 0.035 | 0.04 | 0.00
torso angle min -0.851, max -0.005 rad; torso height min 1.18, max 1.25 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.00 of the steps, 0 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
hip_R: 0.00
knee_R: 0.00
ankle_R: 0.00
hip_L: 0.00
knee_L: 0.00
ankle_L: 0.00

## Round 4: your reply

# Round 4: restore the stabilising balance sign and decouple the hips from the torso

## What round 3 showed

- **The balance sign in rounds 0 to 2 was right, and round 3 broke it.** Round 3 died in 0.06 s, before either foot touched down. The hip bias was −0.55 per hip, and the obs[1] and obs[10] gains were positive.
  - A negative hip torque drove obs[1] negative.
  - That made the hip torque more negative, a runaway loop.
  - The torso centre also moved towards −x, so negative obs[1] is a backward lean.
- **The brief's conventions match all the data.**
  - A positive obs[1] means a forward lean.
  - A negative thigh angle swings the leg backwards.
  - A negative hip torque pitches the torso back.
  - The leg's world angle, with foot-forward positive, is φ = obs[thigh] − obs[1].
  - Upright feedback must have negative gain on obs[1] and obs[10].
- **Why rounds 0 to 2 still drifted backwards.** Each hip tracked a joint-angle target with a large negative constant. In double stance this works like a constant negative torque on the torso. That torque fought a weak balance term, so the torso settled at about −0.45 and the feet ended up well ahead of the hip.

## Design for round 4

1. **Hips track the leg's world angle, not the joint angle.** The hip torque is:
   τ = Kp·(φ* − (q − β)) − Kd·(q̇ − β̇) − Kb·(β − β*) − Kbd·β̇
   with Kp = 1, Kd = 0.1, Kb = 2, Kbd = 0.25.
   - With symmetric leg targets, the tracking terms cancel across the two planted legs, so the torso settles at β* instead of being dragged back.
   - The net gain is −1.0 on obs[1] and −0.15 on obs[10]. The stance leg gives −2, so the loop is clearly stabilising.
2. **Leg target and lean target.**
   - The leg follows φ* = −0.08 + 0.16·cos φ, so the stance phase runs from +0.08 (foot ahead) to −0.24 (push-off). On average the feet are slightly behind the hip, which tips the robot forward.
   - The torso target is a small backward lean, β* = −0.07 − 0.1·v. Leaning back is the only way a thigh limited to ≤ 0 can put the foot ahead.
   - With these targets the thighs stay in about [−0.36, −0.04], clear of the 0 limit.
   - Speed control: going too fast leans the torso further back, and going too slow or backwards leans it forward.
   - The bias is Kp·(−0.08) + Kb·(−0.07) = −0.22.
3. **Knee target: −0.2 + 0.55·sin(φ + 0.3), Kp = 1.5.**
   - In stance the knee is held straight against its limit.
   - It flexes to about −0.75 early in the swing and is almost straight at foot strike.
4. **Frequency 0.9 Hz, symmetric start.** The oscillators start at π/2 and 3π/2, so both hips get the same opening torque. The ankles keep their soft PD.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.22, "a1": -0.3, "a3": -0.22, "a4": -0.3},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.16, "obs[2]": -1.0, "obs[1]": -1.0, "obs[11]": -0.1, "obs[10]": -0.15, "obs[8]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.79, "cos(R)": 0.24, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.16, "obs[5]": -1.0, "obs[1]": -1.0, "obs[14]": -0.1, "obs[10]": -0.15, "obs[8]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.79, "cos(L)": 0.24, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

**What to change in round 5:**
- If the torso still settles well below −0.2 and the robot drifts backwards, I'll make the leg centre c more negative and β* less negative.
- If it now falls forward, I'll do the opposite.

## Round 4: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.11 | 1.86 | height too low
1 | -1.12 | 1.82 | torso angle out of range
2 | -1.16 | 2.08 | height too low
3 | -1.09 | 1.89 | torso angle out of range
4 | -1.20 | 2.14 | height too low
5 | -1.06 | 1.92 | torso angle out of range
6 | -1.10 | 1.86 | torso angle out of range
7 | -1.10 | 1.97 | torso angle out of range
8 | -1.08 | 1.91 | torso angle out of range
9 | -1.11 | 1.81 | height too low

Over the 10 episodes: mean d -1.11 m, min -1.20, max -1.06; mean time survived 1.93 s; mean forward speed -0.58 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.308 | 0.048 | 0.48 | 0.27
right leg | -0.582 | 0.011 | 0.32 | 0.00
right foot | -0.124 | 0.094 | 0.04 | 0.00
left thigh | -0.377 | 0.024 | 0.55 | 0.28
left leg | -0.561 | 0.022 | 0.33 | 0.00
left foot | -0.193 | 0.186 | 0.05 | 0.00
torso angle min -0.999, max -0.005 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.73 of the steps, 13 touchdowns
left foot: on the ground 0.72 of the steps, 10 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.03 | 1.20 | -0.164 | yes | yes | 2.16, 5.30
0.20 | -0.05 | 1.20 | -0.176 | yes | yes | 2.70, 5.84
0.30 | -0.08 | 1.20 | -0.209 | no | yes | 3.29, 0.15
0.40 | -0.12 | 1.20 | -0.350 | no | yes | 3.83, 0.69
0.50 | -0.14 | 1.19 | -0.360 | no | yes | 4.42, 1.28
0.60 | -0.15 | 1.20 | -0.315 | yes | yes | 4.96, 1.82
0.70 | -0.16 | 1.20 | -0.272 | yes | yes | 5.55, 2.41
0.80 | -0.18 | 1.20 | -0.226 | yes | yes | 6.09, 2.95
0.90 | -0.22 | 1.20 | -0.310 | yes | no | 0.40, 3.54
1.00 | -0.27 | 1.19 | -0.399 | yes | no | 0.94, 4.08
1.10 | -0.30 | 1.18 | -0.366 | yes | no | 1.53, 4.67
1.20 | -0.34 | 1.18 | -0.341 | yes | yes | 2.07, 5.22
1.30 | -0.41 | 1.16 | -0.350 | yes | yes | 2.66, 5.80
1.40 | -0.49 | 1.16 | -0.388 | no | yes | 3.20, 0.06

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
hip_R: 0.01
knee_R: 0.00
ankle_R: 0.00
hip_L: 0.02
knee_L: 0.00
ankle_L: 0.00

## Now: round 5 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). This is the last round: this design is final and is the one scored. You may resubmit an earlier design unchanged by copying
its spec.
