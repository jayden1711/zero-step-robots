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

Round 0 is a conservative antiphase gait. Each joint tracks a phase-dependent target through a PD term, which is linear in obs and in the oscillator cos/sin. The thighs also carry torso-balance feedback.

**Structure**
- **Oscillators:** R and L, 0.8 Hz, coupled both ways with lag π. They start at π/2 and 3π/2, so the right leg starts in mid-stance and the left in mid-swing.
- **Thigh (a0, a3):**
  - Target is −0.35 + 0.35·cos φ. The thigh is forward (0) at touchdown (φ = 0) and back (−0.7) at liftoff (φ = π).
  - The PD term is Kp = 2, Kd = 0.2.
  - Balance adds −1.0·(obs[1] − 0.2) − 0.3·obs[10], holding a slight forward lean of 0.2 rad.
  - The bias is 2·(−0.35) + 1.0·0.2 = −0.5.
- **Knee (a1, a4):**
  - Target is −0.5 + 0.6·sin(φ + 0.8) = −0.5 + 0.418 sin φ + 0.430 cos φ.
  - This keeps the knee near straight through stance, peaks the flexion just after liftoff, and re-extends it before touchdown.
  - The PD term is Kp = 3, Kd = 0.15, with bias 3·(−0.5) = −1.5.
- **Foot (a2, a5):** a PD term holds it flat at 0.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.5, "a1": -1.5, "a3": -0.5, "a4": -1.5},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.7, "obs[2]": -2.0, "obs[11]": -0.2, "obs[1]": -1.0, "obs[10]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.7, "obs[5]": -2.0, "obs[14]": -0.2, "obs[1]": -1.0, "obs[10]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 1.254, "cos(R)": 1.29, "obs[3]": -3.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 1.254, "cos(L)": 1.29, "obs[6]": -3.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.37 | 0.70 | torso angle out of range
1 | -0.38 | 0.70 | torso angle out of range
2 | -0.42 | 0.82 | torso angle out of range
3 | -0.36 | 0.70 | torso angle out of range
4 | -0.34 | 0.69 | torso angle out of range
5 | -0.34 | 0.68 | torso angle out of range
6 | -0.37 | 0.69 | torso angle out of range
7 | -0.31 | 0.70 | torso angle out of range
8 | -0.35 | 0.78 | torso angle out of range
9 | -0.37 | 0.69 | torso angle out of range

Over the 10 episodes: mean d -0.36 m, min -0.42, max -0.31; mean time survived 0.71 s; mean forward speed -0.50 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.469 | -0.001 | 0.98 | 0.94
right leg | -1.068 | 0.003 | 0.67 | 0.19
right foot | -0.019 | 0.142 | 0.40 | 0.00
left thigh | -0.820 | 0.029 | 0.95 | 0.89
left leg | -0.806 | 0.008 | 0.88 | 0.60
left foot | -0.049 | 0.205 | 0.61 | 0.11
torso angle min -0.995, max -0.005 rad; torso height min 1.11, max 1.25 m
right foot: on the ground 0.27 of the steps, 3 touchdowns
left foot: on the ground 0.78 of the steps, 9 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.09 | 1.18 | -0.460 | yes | yes | 2.09, 5.24
0.20 | -0.12 | 1.18 | -0.506 | yes | yes | 2.58, 5.72
0.30 | -0.19 | 1.16 | -0.649 | no | yes | 3.10, 6.24
0.40 | -0.26 | 1.15 | -0.790 | no | yes | 3.58, 0.44
0.50 | -0.30 | 1.14 | -0.861 | no | no | 4.10, 0.96
0.60 | -0.33 | 1.13 | -0.871 | no | yes | 4.59, 1.45

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.68
L_thigh_pd_balance: 0.49
R_knee_pd: 0.00
L_knee_pd: 0.06
R_foot_pd: 0.00
L_foot_pd: 0.00

## Round 1: your reply

Round 0 fell backward in about 0.1 s, before any gait started. I think there were two causes:

- **Thigh bias:** both thighs started with a −0.5 bias torque. When the feet touched down, the reaction pitched the torso backward. The balance gain of 1.0 was too weak to fight the PD term and the bias, so both thigh units saturated.
- **Left knee:** at φ = 3π/2 its command came out near −2.75, clipped to −1. The knee collapsed at the start.

**Revisions**
- **Thigh balance is now dominant:** −3.0·(obs[1] − 0.1) − 0.6·obs[10].
  - The rhythmic PD is weaker: Kp = 1.5, Kd = 0.15.
  - The thigh target is −0.25 + 0.3·cos φ.
  - The net bias is nearly zero: −0.375 + 0.3 = −0.075.
- **Knee:**
  - The target is −0.4 + 0.5·sin(φ + 0.8), giving 0.697·sin φ + 0.717·cos φ.
  - The PD term is Kp = 2, Kd = 0.1, with bias −0.8, so the knee stays near straight in stance.
- **Frequency:** slightly faster, at 0.9 Hz.
- **Unit ranges:** widened so the balance term stays linear over its useful range.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.075, "a1": -0.8, "a3": -0.075, "a4": -0.8},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -3.0, "obs[10]": -0.6},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -3.0, "obs[10]": -0.6},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.697, "cos(R)": 0.717, "obs[3]": -2.0, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.697, "cos(L)": 0.717, "obs[6]": -2.0, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.04 | 1.06 | torso angle out of range
1 | -1.05 | 1.08 | torso angle out of range
2 | -1.05 | 1.06 | torso angle out of range
3 | -1.04 | 1.05 | torso angle out of range
4 | -1.04 | 1.06 | torso angle out of range
5 | -1.05 | 1.08 | torso angle out of range
6 | -1.04 | 1.06 | torso angle out of range
7 | -1.06 | 1.08 | torso angle out of range
8 | -1.04 | 1.08 | torso angle out of range
9 | -1.04 | 1.06 | torso angle out of range

Over the 10 episodes: mean d -1.04 m, min -1.06, max -1.04; mean time survived 1.07 s; mean forward speed -0.98 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.120 | 0.043 | 0.81 | 0.54
right leg | -0.596 | 0.003 | 0.44 | 0.00
right foot | -0.096 | 0.162 | 0.10 | 0.00
left thigh | -0.103 | 0.049 | 0.98 | 0.89
left leg | -0.645 | 0.002 | 0.42 | 0.01
left foot | -0.063 | 0.186 | 0.09 | 0.00
torso angle min -0.989, max -0.005 rad; torso height min 0.86, max 1.25 m
right foot: on the ground 0.74 of the steps, 8 touchdowns
left foot: on the ground 0.77 of the steps, 3 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.05 | 1.20 | -0.171 | yes | yes | 2.16, 5.30
0.20 | -0.09 | 1.19 | -0.230 | yes | yes | 2.70, 5.84
0.30 | -0.16 | 1.18 | -0.314 | no | yes | 3.29, 0.15
0.40 | -0.22 | 1.18 | -0.336 | no | yes | 3.83, 0.69
0.50 | -0.29 | 1.18 | -0.308 | yes | yes | 4.42, 1.28
0.60 | -0.39 | 1.15 | -0.380 | yes | yes | 4.96, 1.82
0.70 | -0.52 | 1.11 | -0.523 | yes | no | 5.55, 2.41
0.80 | -0.64 | 1.09 | -0.594 | yes | no | 6.09, 2.95
0.90 | -0.78 | 1.05 | -0.655 | yes | yes | 0.40, 3.54
1.00 | -0.95 | 0.94 | -0.861 | no | yes | 0.94, 4.08

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.11
L_thigh_pd_balance: 0.03
R_knee_pd: 0.00
L_knee_pd: 0.00
R_foot_pd: 0.00
L_foot_pd: 0.00

## Round 2: your reply

Round 2 flips the sign of the torso-balance feedback at the thighs. Round 0 and round 1 both fell the same way, so I think round 1's feedback was pushing the torso further over instead of catching it.

**Why the sign was wrong**
- **Shared joint axis:** in the Walker2d model, the torso's angle and the thigh joints rotate about the same axis.
- **Torque reaction:** with a foot planted, a torque +τ at the thigh puts −τ on the torso, about that same axis. So a positive thigh torque lowers obs[1], and a negative thigh torque raises it.
- **Round 1 data agrees:**
  - obs[1] went negative, so the old term −3·obs[1] gave a large positive thigh torque.
  - That torque drove obs[1] further negative. This is positive feedback.
  - That explains why stronger "balance" in round 1 only slowed the fall.
- **Thigh PD term:** with the leg fixed, a torso tilt θ changes the thigh angle by about −θ. So the term −Kp·obs[2] already adds +Kp·θ, which restores. The old −3θ outweighed it, leaving a net −1.5θ.

This reasoning conflicts with the design hint ("feedback opposes the sign of obs[1] at the stance thigh"). The data from both rounds supports the flip, so I'm following the data.

**Revisions**
- **Thigh balance is now +3.0·obs[1] + 0.5·obs[10].** With the PD term, the net restoring stiffness is about 4.5·θ.
- **Lean setpoint is 0 for now.** It's still unclear which sign of obs[1] means forward. Next round I'll set the lean from the measured speed.
- **Thigh target offset is smaller:** the target is −0.15 + 0.3·cos φ, so the thigh bias is −0.225. The PD and rhythm are unchanged at Kp = 1.5, Kd = 0.15.
- **Knee, foot and oscillators:** unchanged from round 1.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.225, "a1": -0.8, "a3": -0.225, "a4": -0.8},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": 3.0, "obs[10]": 0.5},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": 3.0, "obs[10]": 0.5},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.697, "cos(R)": 0.717, "obs[3]": -2.0, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.697, "cos(L)": 0.717, "obs[6]": -2.0, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.07 | 0.05 | torso angle out of range
1 | -0.07 | 0.05 | torso angle out of range
2 | -0.08 | 0.06 | torso angle out of range
3 | -0.07 | 0.05 | torso angle out of range
4 | -0.07 | 0.05 | torso angle out of range
5 | -0.06 | 0.05 | torso angle out of range
6 | -0.07 | 0.05 | torso angle out of range
7 | -0.08 | 0.06 | torso angle out of range
8 | -0.07 | 0.05 | torso angle out of range
9 | -0.07 | 0.05 | torso angle out of range

Over the 10 episodes: mean d -0.07 m, min -0.08, max -0.06; mean time survived 0.05 s; mean forward speed -1.40 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.781 | -0.005 | 0.87 | 0.83
right leg | 0.003 | 0.006 | 0.21 | 0.00
right foot | -0.001 | 0.011 | 0.06 | 0.00
left thigh | -0.696 | 0.001 | 0.87 | 0.83
left leg | -0.170 | 0.002 | 0.76 | 0.17
left foot | 0.000 | 0.019 | 0.09 | 0.00
torso angle min -0.692, max -0.005 rad; torso height min 1.20, max 1.25 m
right foot: on the ground 0.00 of the steps, 0 touchdowns
left foot: on the ground 0.00 of the steps, 0 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.33
L_thigh_pd_balance: 0.33
R_knee_pd: 0.00
L_knee_pd: 0.00
R_foot_pd: 0.00
L_foot_pd: 0.00

## Now: round 3 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
