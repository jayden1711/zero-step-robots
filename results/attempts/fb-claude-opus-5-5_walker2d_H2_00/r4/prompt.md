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

This first design is a PD-tracking CPG gait with torso balance feedback.

**Structure**
- **Oscillators.** Two oscillators, R and L, run at 0.9 Hz. They are coupled both ways with a lag of π, so the legs settle in antiphase. R starts at phase 0 and L at π.
- **Stance and swing.** Each leg is in stance while φ ∈ [0, π] and in swing while φ ∈ [π, 2π].
- **Joint tracking.** Each joint has one linear unit that acts as a PD controller following a sinusoidal reference. The torque is Kp·(ref(φ) − q) − Kd·q̇, and the constant part Kp·offset goes into `bias`. The references are:
  - Thigh: q_ref = −0.25 + 0.25·cos φ. It goes from 0 (forward) to −0.5 (back) during stance and returns during swing. Kp = 2, Kd = 0.4.
  - Knee: q_ref = −0.4 + 0.4·sin φ. The knee is straight at mid-stance and flexed to −0.8 at mid-swing, for ground clearance. Kp = 2, Kd = 0.15.
  - Foot: q_ref = 0. Kp = 1, Kd = 0.03. The foot stays roughly flat and pushes off passively as the stance leg extends back.
- **Torso balance.** Both thigh units also receive −1.0·obs[1] − 0.1·obs[10]. A negative hip torque pitches the torso backward, so this term opposes forward lean and forward pitch rate. In stance, the joint-space thigh PD also helps keep the torso upright.
- **Scale.** Gains are in action units, so 1 = 100 Nm. They are sized against the estimated segment inertias, roughly 3.7 kg·m² for a whole leg about the hip, to stay moderately damped.

**What I will watch for in the results**
- The sign of obs[1].
- Whether the robot falls forward or backward.
- Whether it walks in place.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.5, "a1": -0.8, "a2": 0.0, "a3": -0.5, "a4": -0.8, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.5, "obs[2]": -2.0, "obs[11]": -0.4, "obs[1]": -1.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.8, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.5, "obs[5]": -2.0, "obs[14]": -0.4, "obs[1]": -1.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.8, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.17 | 0.27 | torso angle out of range
1 | -0.16 | 0.26 | torso angle out of range
2 | -0.18 | 0.30 | torso angle out of range
3 | -0.18 | 0.28 | torso angle out of range
4 | -0.17 | 0.28 | torso angle out of range
5 | -0.17 | 0.29 | torso angle out of range
6 | -0.17 | 0.27 | torso angle out of range
7 | -0.18 | 0.29 | torso angle out of range
8 | -0.17 | 0.27 | torso angle out of range
9 | -0.17 | 0.27 | torso angle out of range

Over the 10 episodes: mean d -0.17 m, min -0.18, max -0.16; mean time survived 0.28 s; mean forward speed -0.63 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.976 | 0.022 | 0.91 | 0.74
right leg | -0.277 | 0.003 | 0.88 | 0.50
right foot | -0.000 | 0.214 | 0.14 | 0.00
left thigh | -0.641 | 0.016 | 0.99 | 0.97
left leg | -0.736 | 0.002 | 0.79 | 0.15
left foot | 0.000 | 0.230 | 0.13 | 0.00
torso angle min -1.000, max -0.005 rad; torso height min 1.12, max 1.25 m
right foot: on the ground 0.68 of the steps, 4 touchdowns
left foot: on the ground 0.65 of the steps, 5 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 0.00, 3.14
0.10 | -0.07 | 1.18 | -0.498 | yes | no | 0.59, 3.73
0.20 | -0.14 | 1.13 | -0.877 | yes | yes | 1.13, 4.27

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_pd_balance: 0.56
R_knee_pd: 0.24
R_foot_pd: 0.00
L_thigh_pd_balance: 0.68
L_knee_pd: 0.00
L_foot_pd: 0.00

## Round 1: your reply

Round 0 failed because the controller drove the torso backward. Both thigh torques sat at about −1 (the bias of −0.5 plus the reference offset). With the feet on the ground, that pitched the torso back to −1 rad within 0.27 s. The data agree with the stated sign conventions:

- x moved −0.17 m. That equals 0.2·sin(1), the arc of the torso root rotating about the hip.
- The stance thigh angle followed the torso angle (q ≈ θ ≈ −1).

The damping was also too stiff for the light torso at dt = 0.008, so the thighs were saturated most of the time.

**Changes**

- **Thigh tracks the absolute leg angle.** Each thigh now tracks α = q − θ, the leg angle in the world frame, instead of the joint angle. The damping uses q̇ − θ̇. In stance α is fixed by the ground, so this tracking no longer adds stiffness or damping to the torso's fast mode.
- **Torso balance is a separate PD.** It holds the torso at θref = −0.2 (slight backward lean). Because the thigh can't go in front of the torso axis (q ≤ 0), this lean is what lets the swing foot land ahead of the hip: α ≤ −θ. The gains are Kt = 1.5 and Ktd = 0.07 per leg, sized so the torso mode stays well damped and stable at dt = 0.008.
- **Leg reference.** α_ref = −0.05 + 0.25·cos φ, which runs from +0.2 to −0.3 rad. Combined thigh coefficients:
  - q: −1
  - θ: Kp − Kt = −0.5
  - q̇: −0.3
  - θ̇: Kd − Ktd = +0.23
  - constant (bias): Kp·α0 + Kt·θref = −0.35
- **Starting phases.** R = π/2 (mid-stance) and L = 3π/2 (mid-swing). At these phases the initial references match the straight-leg start, so there is no large torque at t = 0.
- **Other settings.** The knee is unchanged. The foot damping is reduced. The frequency is 0.8 Hz.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.35, "a1": -0.8, "a2": 0.0, "a3": -0.35, "a4": -0.8, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_abs_torso",
    "inputs": {"cos(R)": 0.25, "obs[2]": -1.0, "obs[1]": -0.5, "obs[11]": -0.3, "obs[10]": 0.23},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.8, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_abs_torso",
    "inputs": {"cos(L)": 0.25, "obs[5]": -1.0, "obs[1]": -0.5, "obs[14]": -0.3, "obs[10]": 0.23},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.8, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.72 | 1.00 | torso angle out of range
1 | -0.65 | 0.93 | torso angle out of range
2 | -0.73 | 1.02 | torso angle out of range
3 | -0.72 | 0.97 | torso angle out of range
4 | -0.81 | 1.05 | torso angle out of range
5 | -0.75 | 1.02 | torso angle out of range
6 | -0.77 | 0.99 | torso angle out of range
7 | -0.71 | 0.99 | torso angle out of range
8 | -0.67 | 0.99 | torso angle out of range
9 | -0.75 | 0.98 | torso angle out of range

Over the 10 episodes: mean d -0.73 m, min -0.81, max -0.65; mean time survived 0.99 s; mean forward speed -0.73 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.832 | 0.017 | 0.69 | 0.43
right leg | -0.714 | 0.003 | 0.62 | 0.24
right foot | -0.057 | 0.133 | 0.06 | 0.00
left thigh | -0.741 | 0.021 | 0.69 | 0.42
left leg | -0.736 | 0.002 | 0.61 | 0.26
left foot | -0.073 | 0.188 | 0.09 | 0.00
torso angle min -0.987, max -0.005 rad; torso height min 1.03, max 1.25 m
right foot: on the ground 0.44 of the steps, 17 touchdowns
left foot: on the ground 0.78 of the steps, 5 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.09 | 1.15 | -0.768 | yes | yes | 2.09, 5.24
0.20 | -0.12 | 1.16 | -0.719 | yes | yes | 2.58, 5.72
0.30 | -0.10 | 1.19 | -0.273 | yes | yes | 3.10, 6.24
0.40 | -0.16 | 1.17 | -0.480 | no | yes | 3.58, 0.44
0.50 | -0.27 | 1.12 | -0.919 | no | yes | 4.10, 0.96
0.60 | -0.35 | 1.14 | -0.796 | no | yes | 4.59, 1.45
0.70 | -0.40 | 1.15 | -0.600 | no | yes | 5.11, 1.97
0.80 | -0.47 | 1.13 | -0.575 | yes | yes | 5.59, 2.45
0.90 | -0.59 | 1.10 | -0.626 | yes | no | 6.11, 2.97

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
R_thigh_abs_torso: 0.02
R_knee_pd: 0.00
R_foot_pd: 0.00
L_thigh_abs_torso: 0.04
L_knee_pd: 0.00
L_foot_pd: 0.00

## Round 2: your reply

## Round 2 design: one shared torso torque plus a scissor term between the legs

**Why round 1 failed.** Round 1 made each thigh track its own leg-angle reference. During stance, driving the planted leg backward needs a negative hip torque, and that torque pitches the torso backward. So the leg-tracking error added to the torso balance term and shifted its equilibrium:

- The stance leg's tracking error reached about 0.5 rad.
- Divided by Kt = 1.5, that moves the torso equilibrium from −0.2 to about −0.55 rad.
- With both legs on the ground, both hips pulled the same way.

This matches the torso angles of −0.7 to −0.9 rad and the backward drift.

**Fix.** The torso pitch torque equals τ_R + τ_L, because each hip's reaction torque acts on the torso. I split the two hip torques into a common part and a differential part. This needs no stance/swing gating.

- **Torso balance (common mode).** τ_torso = −3(θ − θref) − 0.16·θ̇, with θref = −0.2. Half goes to each hip. This is the only net torque on the torso.
  - At about 40 rad/s on a torso of roughly 0.19 kg·m², damping is close to critical.
  - The −0.2 rad backward lean is still needed, because q ≤ 0 means a foot can only land ahead of the hip by about −θ.
- **Scissor (differential mode).** A torque of +K(δref − δ) − D·δ̇ goes to the right hip and the opposite to the left, with δ = q_R − q_L and δref = 0.5·cos φ_R.
  - θ cancels out of δ.
  - Because the two parts cancel, this term puts zero net torque on the torso.
  - With the stance foot planted, it swings the swing leg forward relative to the stance leg.
  - Gains: K = 1.5, D = 0.2.
- **Knee.** A stiff PD holds the knee straight. A phase reflex adds strong flexion during swing (sin φ < −0.3).
  - In swing the total knee torque is about −1.0, settling near −0.67 rad.
  - In stance it is about +0.2, pressing the knee against its straight limit for support.
- **Feet and phases.** The feet keep the same PD. The starting phases stay at π/2 and 3π/2, where δref = 0 matches the initial pose.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.3, "a1": -0.4, "a2": 0.0, "a3": -0.3, "a4": -0.4, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_common",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.16},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": 0.5}},
   {"type": "linear", "name": "hip_scissor_diff",
    "inputs": {"cos(R)": 0.375, "cos(L)": -0.375, "obs[2]": -1.5, "obs[5]": 1.5, "obs[11]": -0.2, "obs[14]": 0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"sin(R)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a1": -0.6}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"sin(L)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a4": -0.6}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.06 | 1.18 | height too low
1 | -1.08 | 1.17 | height too low
2 | -1.07 | 1.19 | height too low
3 | -1.08 | 1.18 | height too low
4 | -1.07 | 1.19 | height too low
5 | -1.07 | 1.19 | height too low
6 | -1.06 | 1.17 | height too low
7 | -1.07 | 1.19 | height too low
8 | -1.08 | 1.18 | height too low
9 | -1.07 | 1.18 | height too low

Over the 10 episodes: mean d -1.07 m, min -1.08, max -1.06; mean time survived 1.18 s; mean forward speed -0.91 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.236 | 0.027 | 0.59 | 0.27
right leg | -0.538 | 0.011 | 0.27 | 0.00
right foot | -0.133 | 0.105 | 0.05 | 0.00
left thigh | -0.157 | 0.035 | 0.44 | 0.01
left leg | -0.600 | 0.004 | 0.29 | 0.01
left foot | -0.076 | 0.177 | 0.07 | 0.00
torso angle min -0.965, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.71 of the steps, 7 touchdowns
left foot: on the ground 0.82 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.04 | 1.20 | -0.189 | yes | yes | 2.09, 5.24
0.20 | -0.07 | 1.20 | -0.277 | yes | yes | 2.58, 5.72
0.30 | -0.09 | 1.20 | -0.245 | yes | yes | 3.10, 6.24
0.40 | -0.12 | 1.20 | -0.201 | yes | yes | 3.58, 0.44
0.50 | -0.19 | 1.19 | -0.255 | yes | yes | 4.10, 0.96
0.60 | -0.25 | 1.19 | -0.281 | no | yes | 4.59, 1.45
0.70 | -0.34 | 1.17 | -0.354 | yes | yes | 5.11, 1.97
0.80 | -0.45 | 1.14 | -0.469 | yes | yes | 5.59, 2.45
0.90 | -0.60 | 1.08 | -0.594 | yes | no | 6.11, 2.97
1.00 | -0.73 | 1.06 | -0.562 | yes | no | 0.31, 3.46
1.10 | -0.92 | 0.95 | -0.739 | no | yes | 0.84, 3.98

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance_common: 0.00
hip_scissor_diff: 0.00
R_knee_pd: 0.00
L_knee_pd: 0.00
R_foot_pd: 0.00
L_foot_pd: 0.00

## Round 3: your reply

## Round 3: lean forward, a stronger scissor, and ankle push-off

**Why rounds 1 and 2 drifted backward.** In round 2 the torso controller worked: it held θ near the −0.2 target from 0.1 to 0.4 s. Yet x fell steadily even while both feet were down, and it then sped up into a backward fall. The likely cause is the foot geometry. Walker2d's foot extends forward from the ankle, so the heel is at the ankle and the base of support runs from the ankle to about 0.2 m ahead of it. At the start the centre of mass sits right over the heel. Commanding a backward lean pushed it behind the support, and nothing could stop the backward fall. The robot was also not really stepping: the thighs moved only 0.24 rad because the scissor was too weak for legs of about 9.5 kg.

**Changes**

- **Torso target is now slightly forward, with speed regulation.**
  - θref = 0.05 − 0.15·v, where v = obs[8].
  - At rest the torso leans slightly forward, which shifts weight over the feet and starts forward motion.
  - If the robot speeds up, the target leans back. That lets the swing foot land further ahead (α ≤ −θ), which brakes the fall.
  - If it moves backward, the target leans forward.
  - Same common-mode PD as round 2 (Kt = 3, Ktd = 0.16). It adds −0.45·obs[8], with a bias of +0.075 per hip.
- **Scissor about twice as stiff, with more amplitude.** δref = 0.6·cos φ_R, K = 3, D = 0.3.
  - For one swinging leg (I ≈ 3.7, gravity stiffness about 0.47 per rad), this gives ω_n ≈ 9.7 rad/s and ζ ≈ 0.4.
  - The gait drives it at 5.65 rad/s (0.9 Hz), so the tracking lag stays modest.
  - It still puts zero net torque on the torso.
- **Ankle push-off reflex.** In late stance (sin φ − cos φ > 0.8, roughly φ ∈ [1.4, 3.3]) the foot gets −0.25, which presses the toe down for propulsion. Elsewhere it gets 0, because the bias cancels the reflex's off-state.
- **Unchanged.** The knee PD and the swing-flexion reflex stay the same. The frequency rises to 0.9 Hz for quicker catching steps.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.075, "a1": -0.4, "a2": -0.125, "a3": 0.075, "a4": -0.4, "a5": -0.125},
 "units": [
   {"type": "linear", "name": "torso_balance_common_speed",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.16, "obs[8]": -0.45},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": 0.5}},
   {"type": "linear", "name": "hip_scissor_diff",
    "inputs": {"cos(R)": 0.9, "cos(L)": -0.9, "obs[2]": -3.0, "obs[5]": 3.0, "obs[11]": -0.3, "obs[14]": 0.3},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"sin(R)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a1": -0.6}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"sin(L)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a4": -0.6}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "R_foot_pushoff",
    "inputs": {"sin(R)": 1.0, "cos(R)": -1.0}, "threshold": 0.8, "sharpness": 4.0,
    "to": {"a2": -0.125}},
   {"type": "reflex", "name": "L_foot_pushoff",
    "inputs": {"sin(L)": 1.0, "cos(L)": -1.0}, "threshold": 0.8, "sharpness": 4.0,
    "to": {"a5": -0.125}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -1.00 | 0.90 | height too low
1 | -1.01 | 0.91 | height too low
2 | -1.01 | 0.91 | height too low
3 | -1.00 | 0.90 | height too low
4 | -1.02 | 0.92 | height too low
5 | -1.03 | 0.93 | height too low
6 | -1.01 | 0.90 | height too low
7 | -1.03 | 0.93 | height too low
8 | -1.02 | 0.92 | height too low
9 | -1.00 | 0.90 | height too low

Over the 10 episodes: mean d -1.01 m, min -1.03, max -1.00; mean time survived 0.91 s; mean forward speed -1.11 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
right thigh | -0.211 | 0.044 | 0.71 | 0.50
right leg | -0.412 | 0.012 | 0.30 | 0.00
right foot | -0.204 | 0.063 | 0.08 | 0.00
left thigh | -0.086 | 0.024 | 0.73 | 0.50
left leg | -0.553 | 0.014 | 0.37 | 0.01
left foot | -0.350 | 0.171 | 0.07 | 0.00
torso angle min -0.867, max -0.005 rad; torso height min 0.81, max 1.25 m
right foot: on the ground 0.89 of the steps, 2 touchdowns
left foot: on the ground 0.80 of the steps, 2 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | right foot contact | left foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | no | 1.57, 4.71
0.10 | -0.03 | 1.21 | -0.137 | yes | yes | 2.16, 5.30
0.20 | -0.08 | 1.20 | -0.241 | yes | yes | 2.70, 5.84
0.30 | -0.15 | 1.20 | -0.249 | yes | yes | 3.29, 0.15
0.40 | -0.23 | 1.19 | -0.251 | yes | yes | 3.83, 0.69
0.50 | -0.35 | 1.16 | -0.358 | yes | yes | 4.42, 1.28
0.60 | -0.48 | 1.12 | -0.466 | yes | yes | 4.96, 1.82
0.70 | -0.64 | 1.04 | -0.648 | yes | yes | 5.55, 2.41
0.80 | -0.81 | 0.94 | -0.808 | yes | no | 6.09, 2.95

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_balance_common_speed: 0.00
hip_scissor_diff: 0.00
R_knee_pd: 0.00
L_knee_pd: 0.00
R_foot_pd: 0.00
L_foot_pd: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
