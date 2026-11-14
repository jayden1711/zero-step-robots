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

This first design is a two-oscillator walking gait with per-joint PD control on top. It uses 6 of the 16 hidden units and leaves 10 free for later revisions.

**Rhythm.** There are oscillators `R` and `L` at 1.0 Hz, coupled with weight 4 and lag π each way. They start at phases 0 and π: the right leg starts at touchdown and the left leg at lift-off. For each leg, stance is phase 0 to π (sin > 0) and swing is π to 2π (sin < 0).

**Hip (one unit per leg).**
- **Target:** the thigh angle follows q = −0.25 + 0.25·cos φ, so the thigh is at 0 at touchdown and at −0.5 at lift-off.
- **PD:** Kp = 1, Kd = 0.05.
- **Feedforward:** a torque of −0.3·sin φ. Because the legs are in antiphase, the two legs' feedforward torques cancel at the torso: the swing leg is pulled forward and the stance leg pushed back without pitching the torso.
- **Balance:** the hip torque includes −1.0·obs[1] − 0.05·obs[10], which opposes the torso angle and angular velocity, as the hint says.
- **Speed:** a −0.2·obs[8] term makes the torso lean back as speed rises. Leaning back puts the feet further forward, which brakes. With the bias, this aims for about 0.8 m/s.
- **Gains kept small:** the torso is light (about 0.2 kg·m² about the hip). Large damping gains would be numerically unstable with the 8 ms control step.

**Knee.**
- **Target:** −0.25 + 0.55·sin φ + 0.23·cos φ, which equals −0.25 + 0.6·sin(φ + 0.4).
- **Stance:** the target is above the 0 limit, so the knee pushes straight.
- **Swing:** the knee flexes most early in the swing, then straightens again before touchdown.
- **Gains:** Kp = 1.5, Kd = 0.1.

**Ankle.**
- **Flat foot:** a gain of 0.4 keeps the foot level with the ground, using the toe-up angle q_thigh + q_leg + q_foot − θ. Since it targets the ground orientation, it does not fight the ground during stance.
- **Push-off:** a −0.3·sin(φ − π/4) term pushes the toe down late in stance and lifts it during swing.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 4.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 4.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.09, "a1": -0.375, "a3": -0.09, "a4": -0.375},
 "units": [
   {"type": "linear", "name": "R_hip",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.05, "obs[1]": -1.0, "obs[10]": -0.05, "obs[8]": -0.2, "cos(R)": 0.25, "sin(R)": -0.3},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_hip",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.05, "obs[1]": -1.0, "obs[10]": -0.05, "obs[8]": -0.2, "cos(L)": 0.25, "sin(L)": -0.3},
    "range": 2.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.83, "cos(R)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.83, "cos(L)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[1]": 0.4, "obs[2]": -0.4, "obs[3]": -0.4, "obs[4]": -0.4, "obs[13]": -0.02, "sin(R)": -0.21, "cos(R)": 0.21},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[1]": 0.4, "obs[5]": -0.4, "obs[6]": -0.4, "obs[7]": -0.4, "obs[16]": -0.02, "sin(L)": -0.21, "cos(L)": 0.21},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

**What I'll check in the results:**
- **Early falls by torso angle:** that would suggest the stated sign of obs[1] is wrong. The spec's facts don't fully agree with each other on this, so it is my main risk. The fix would be to flip the obs[1] and obs[10] gains at the hips.
- **Falls by height, forward:** the forward drive is too strong. I'd lean the torso back more by lowering the a0 and a3 biases, or raise the speed gain.
- **Little forward progress:** the opposite. I'd raise the thigh amplitude and feedforward, or the target speed.

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.19 | 1.04 | torso angle out of range
1 | -1.16 | 1.00 | torso angle out of range
2 | -1.21 | 1.06 | height too low
3 | -1.21 | 1.06 | height too low
4 | -1.22 | 1.06 | height too low
5 | -1.19 | 1.04 | torso angle out of range
6 | -1.19 | 1.03 | torso angle out of range
7 | -1.20 | 1.05 | height too low
8 | -1.15 | 1.00 | torso angle out of range
9 | -1.20 | 1.04 | torso angle out of range

Over the 10 episodes: mean d -1.19 m, min -1.22, max -1.15; mean time survived 1.04 s; mean forward speed -1.15 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.186 | 0.038 | 0.55 | 0.28
right leg | -0.616 | 0.011 | 0.33 | 0.00
right foot | -0.562 | 0.703 | 0.10 | 0.00
left thigh | -0.162 | 0.041 | 0.63 | 0.06
left leg | -0.717 | 0.026 | 0.32 | 0.00
left foot | -0.842 | 0.823 | 0.12 | 0.00
torso angle min -0.992, max -0.005 rad; torso height min 0.82, max 1.25 m
right foot: on the ground 0.68 of the steps, 5 touchdowns
left foot: on the ground 0.44 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.04 | 1.20 | -0.170 | yes | yes | 0.65, 3.80
0.20 | -0.08 | 1.19 | -0.274 | yes | no | 1.26, 4.40
0.30 | -0.12 | 1.19 | -0.275 | yes | no | 1.91, 5.05
0.40 | -0.18 | 1.18 | -0.225 | yes | no | 2.51, 5.65
0.50 | -0.33 | 1.16 | -0.345 | yes | yes | 3.17, 0.03
0.60 | -0.47 | 1.15 | -0.512 | no | yes | 3.77, 0.63
0.70 | -0.58 | 1.13 | -0.500 | no | yes | 4.42, 1.28
0.80 | -0.74 | 1.09 | -0.576 | yes | yes | 5.03, 1.88
0.90 | -0.94 | 1.01 | -0.763 | yes | no | 5.68, 2.54
1.00 | -1.13 | 0.88 | -0.945 | no | no | 0.00, 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_hip: 0.00
L_hip: 0.00
R_knee: 0.00
L_knee: 0.00
R_foot: 0.00
L_foot: 0.00

## Now: round 1 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
