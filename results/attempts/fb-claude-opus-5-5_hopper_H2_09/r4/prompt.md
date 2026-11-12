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

This first design holds the hopper upright and adds a gentle hop rhythm. It does not try to be fast yet. The rhythm amplitudes are kept moderate, so the round-0 results should mostly show whether the sign conventions and the balance loop are right.

**Oscillator.** One oscillator, `hop`, runs at 2.5 Hz.

**Thigh (a0): torso balance.** The thigh torque is −4·(obs[1] + 0.15·obs[7]). This opposes both the torso tilt and its rate. A bias of +0.12 shifts the balance point to a slight forward lean of about 0.03 rad, which is meant to produce forward drift. There is also a weak hold that keeps the thigh angle near 0, and a small cos-phase swing (0.3) for the flight phase.

**Leg (a1) and foot (a2): posture hold plus rhythm.** Each joint has a stiff hold that keeps its angle near 0 and damps its speed. On top of that, sin(hop) adds an extension push of 0.5 at the leg and 0.3 at the foot. This means the push-off happens a quarter cycle after the thigh swing.

**What I'll adjust next round:**
- If the robot falls forward or backward quickly, I'll fix the lean bias and balance gains.
- If it stands but doesn't move, I'll increase the rhythm amplitudes and the lean.
- If it falls in an oscillating way, I'll lower the frequency or change the phase relationship between the joints.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": 0.12},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 2.0, "tol": 0.02, "to": {"a0": -4.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.5}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.3}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.5, "a2": 0.3}}
 ]}
```

## Round 0: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.15 | 1.14 | torso angle out of range
1 | -0.15 | 1.14 | torso angle out of range
2 | -0.17 | 1.13 | torso angle out of range
3 | -0.17 | 1.13 | torso angle out of range
4 | -0.17 | 1.13 | torso angle out of range
5 | -0.16 | 1.14 | torso angle out of range
6 | -0.16 | 1.14 | torso angle out of range
7 | -0.17 | 1.13 | torso angle out of range
8 | -0.15 | 1.14 | torso angle out of range
9 | -0.15 | 1.14 | torso angle out of range

Over the 10 episodes: mean d -0.16 m, min -0.17, max -0.15; mean time survived 1.14 s; mean forward speed -0.14 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.067 | 0.010 | 0.37 | 0.14
leg | -0.141 | 0.015 | 0.19 | 0.00
foot | -0.078 | 0.055 | 0.11 | 0.00
torso angle min -0.199, max 0.007 rad; torso height min 1.19, max 1.25 m
foot: on the ground 0.93 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.004 | yes | 1.63
0.20 | 0.04 | 1.21 | -0.002 | yes | 3.14
0.30 | 0.06 | 1.22 | -0.013 | yes | 4.78
0.40 | 0.03 | 1.23 | -0.043 | yes | 0.00
0.50 | 0.00 | 1.20 | -0.004 | yes | 1.63
0.60 | 0.00 | 1.21 | -0.011 | yes | 3.14
0.70 | 0.00 | 1.21 | -0.031 | yes | 4.78
0.80 | -0.06 | 1.22 | -0.114 | yes | 6.28
0.90 | -0.09 | 1.21 | -0.077 | yes | 1.63
1.00 | -0.12 | 1.22 | -0.096 | yes | 3.14
1.10 | -0.14 | 1.20 | -0.166 | yes | 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_hold: 0.00
thigh_swing: 0.00
leg_hold: 0.00
foot_hold: 0.00
pushoff: 0.00

## Round 1: your reply

## Round 1: flip the thigh balance sign and stand slightly crouched

**What round 0 shows.** In every episode the torso fell backward. The fall was slow and smooth, and it lined up with the thigh rhythm:

- At oscillator phase 0, cos(hop) = 1 and the thigh swing adds +0.3 to a0. At those moments the torso pitched further back: −0.043 at 0.4 s and −0.114 at 0.8 s.
- At phase ≈ 1.6, cos(hop) ≈ 0 and the swing adds nothing. There the torso recovered toward upright: −0.004 and −0.077.
- The +0.12 bias kept pushing the torso backward from the start.

So in this simulation, **positive thigh torque pitches the torso backward**. That fits the joint mechanics: the hip torque acts as +τ on the thigh and −τ on the torso, and the planted leg barely moves. It contradicts the stated sign fact. As a result, the round-0 balance loop was positive feedback. It saturated (14% of steps at |a0| ≥ 0.99), driving the torso further back.

A second problem: the thigh and leg holds targeted angle 0, which is the joints' upper limit. A positive torque there is partly absorbed by the joint stop.

**Changes:**

1. **Balance sign flipped.** The thigh torque is now a0 = +3·(obs[1] + 0.15·obs[7]). When the torso leans back, this gives a negative thigh torque, which pitches the torso forward.
2. **Forward lean set by a negative bias.** The lean is now produced by a negative bias on a0 instead of a positive one.
3. **Posture moved off the joint limits.** The thigh is held near −0.1 rad and the leg near −0.1 rad, set through the biases. That way torques act in both directions.
4. **Rhythm kept small this round.** The thigh swing is 0.15, the leg push 0.4 and the foot push 0.2. I'll only scale the hop up once standing balance is confirmed.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": -0.11, "a1": -0.2},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 2.0, "tol": 0.02, "to": {"a0": 3.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.5}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.15}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.2}}
 ]}
```

**How to read the round-1 results:**

- If the torso now stays within ±0.1 rad for much longer, the sign flip is confirmed, and next round I'll scale up the hop and the lean for speed.
- If it now falls forward quickly, the flip was wrong. I'll revert to the stated sign and keep the off-limit posture.

## Round 1: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.01 | 0.11 | torso angle out of range
1 | -0.01 | 0.10 | torso angle out of range
2 | 0.01 | 0.21 | torso angle out of range
3 | -0.01 | 0.11 | torso angle out of range
4 | 0.01 | 0.21 | torso angle out of range
5 | -0.01 | 0.14 | torso angle out of range
6 | -0.01 | 0.12 | torso angle out of range
7 | 0.00 | 0.19 | torso angle out of range
8 | -0.01 | 0.10 | torso angle out of range
9 | -0.01 | 0.10 | torso angle out of range

Over the 10 episodes: mean d -0.00 m, min -0.01, max 0.01; mean time survived 0.14 s; mean forward speed -0.05 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.199 | -0.004 | 0.46 | 0.29
leg | -0.011 | 0.005 | 0.10 | 0.00
foot | 0.004 | 0.035 | 0.04 | 0.00
torso angle min -0.169, max -0.005 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.21 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | -0.01 | 1.20 | -0.169 | yes | 1.63

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_hold: 0.00
thigh_swing: 0.00
leg_hold: 0.00
foot_hold: 0.00
pushoff: 0.00

## Round 2: your reply

## Round 2: revert to the stated sign, keep the thigh off its joint stop, and add ankle balance

**What round 1 shows.** Flipping the thigh balance sign was wrong. The torso fell backward in about 0.1 s, ten times faster than in round 0. The thigh torque sat at the action limit on 29% of steps, which means the loop was driving the torso further over. The stated convention holds: negative thigh torque pitches the torso backward. The −0.11 bias made this worse by pushing the torso back from the first step.

**Rereading round 0 with the correct sign.** The backward drift in round 0 was not a sign problem.

- In seed 0, the thigh angle peaked at +0.010 rad. That is at its upper joint limit of 0.
- The balance loop was pushing positive thigh torque into that joint stop. The torque could not rotate the torso relative to the leg, so the whole robot slowly tipped backward as one rigid body. This is why x went negative.

Hip torque alone cannot stop the whole body from tipping while it pivots on the foot. That needs an ankle torque.

**Changes:**

1. **Balance sign reverted.** Thigh torque is now −3·(obs[1] + 0.25·obs[7]). This has more damping than round 0 and a lower gain, so it should saturate less.
2. **Thigh held off its stop.** A thigh hold toward −0.2 rad (gain −1.0, plus a −0.2 bias on a0) leaves room for the balance torque to act in both directions. The +0.12 forward-lean bias is removed. Forward lean waits until standing is confirmed.
3. **New ankle balance.** a2 gets −1.0·(obs[1] + 0.2·obs[7]). By the same reaction rule, positive foot torque pitches the leg forward. So when the robot tips back, the ankle pushes it forward again.
4. **Rhythm kept small.** Thigh swing is 0.1; push-off is 0.3 at the leg and 0.1 at the foot.

**How to read the round-2 results:**

- If the robot now survives several seconds near upright, I'll add forward lean and scale up the hop.
- If it still tips back with the thigh at 0, I'll move the thigh target further negative and raise the ankle gain.
- If it now tips forward, I'll reduce the ankle gain and the thigh offset.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": -0.2, "a1": -0.1},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 3.0, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.1}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 3.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.3, "a2": 0.1}}
 ]}
```

## Round 2: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.04 | 8.00 | cut off at 1000 steps
1 | -0.03 | 8.00 | cut off at 1000 steps
2 | -0.05 | 8.00 | cut off at 1000 steps
3 | -0.05 | 8.00 | cut off at 1000 steps
4 | -0.05 | 8.00 | cut off at 1000 steps
5 | -0.05 | 8.00 | cut off at 1000 steps
6 | -0.04 | 8.00 | cut off at 1000 steps
7 | -0.05 | 8.00 | cut off at 1000 steps
8 | -0.03 | 8.00 | cut off at 1000 steps
9 | -0.04 | 8.00 | cut off at 1000 steps

Over the 10 episodes: mean d -0.04 m, min -0.05, max -0.03; mean time survived 8.00 s; mean forward speed -0.01 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.072 | 0.004 | 0.05 | 0.00
leg | -0.132 | 0.007 | 0.07 | 0.00
foot | 0.004 | 0.056 | 0.09 | 0.00
torso angle min -0.080, max -0.005 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.99 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | -0.016 | yes | 1.63
0.20 | 0.02 | 1.21 | -0.031 | yes | 3.14
0.30 | 0.02 | 1.21 | -0.049 | yes | 4.78
0.40 | -0.00 | 1.21 | -0.058 | yes | 0.00
0.50 | -0.02 | 1.21 | -0.054 | yes | 1.63
0.60 | -0.01 | 1.21 | -0.059 | yes | 3.14
0.70 | -0.01 | 1.21 | -0.069 | yes | 4.78
0.80 | -0.02 | 1.21 | -0.078 | yes | 6.28
0.90 | -0.03 | 1.21 | -0.065 | yes | 1.63
1.00 | -0.01 | 1.21 | -0.066 | yes | 3.14
1.10 | 0.00 | 1.21 | -0.072 | yes | 4.78
1.20 | -0.02 | 1.21 | -0.068 | yes | 6.28
1.30 | -0.03 | 1.21 | -0.058 | yes | 1.63
1.40 | -0.01 | 1.21 | -0.061 | yes | 3.14

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
thigh_hold: 0.00
thigh_swing: 0.00
leg_hold: 0.00
foot_hold: 0.00
ankle_balance: 0.00
pushoff: 0.00

## Round 3: your reply

## Round 3: lean slightly forward, add speed feedback, and make the hop bigger

**What round 2 shows.** The balance loop now works: all 10 episodes survived the full 8 s. But the robot only stands and sways; it does not travel.

- **Steady backward lean.** The torso settled at about −0.065 rad. That is about −0.2 / 3, so the −0.2 bias on a0 against the torso gain of −3 set that lean. The equilibrium lean is roughly the a0 bias divided by the balance gain. That gives me a direct dial for lean.
- **The hop is too weak.** The foot was on the ground on 99% of steps. Each rhythm cycle moved x back and forth by about 2 cm, but with the backward lean there was no net progress.

**Changes:**

1. **Forward lean.** The a0 bias goes from −0.2 to +0.1. With the stronger torso gain below, the target lean is about +0.025 rad when standing still. The ankle balance term still pulls the lean toward 0, so the robot shouldn't run away forward.
2. **Speed regulation through lean.** A new unit adds −0.1·obs[5] to a0. As forward speed rises, the lean target shrinks; at about 1 m/s the lean target is back to upright. This should stop it from accelerating into a forward fall.
3. **Stronger, better-damped balance.** The torso term is now −4·(obs[1] + 0.3·obs[7]). Larger hops will disturb the torso more than standing did.
4. **A real hop.**
   - Leg push-off goes from 0.3 to 0.6, foot from 0.1 to 0.4.
   - Leg stiffness drops from −2 to −1.5, so the rhythm can move the joint further.
   - Thigh swing goes from 0.1 to 0.25.
   - Frequency stays at 2.5 Hz.

**How to read the round-3 results:**

- **Survives and moves forward but slowly:** next round I'll raise the lean bias and hop amplitude.
- **Moves backward:** I'll flip the thigh swing sign (the phase relationship) and add more lean.
- **Falls forward:** I'll cut the bias back to about +0.03 and strengthen the speed term.
- **Falls in an oscillating way:** I'll pull the amplitudes halfway back toward round 2.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": 0.1, "a1": -0.1},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.3},
    "range": 3.0, "tol": 0.02, "to": {"a0": -4.0}},
   {"type": "linear", "name": "speed_lean", "inputs": {"obs[5]": 1.0},
    "range": 5.0, "tol": 0.02, "to": {"a0": -0.1}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.25}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -1.5}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 3.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.6, "a2": 0.4}}
 ]}
```

## Round 3: test results of that design

Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).

Per episode:
seed | d (m) | time survived (s) | how it ended
0 | -0.08 | 1.18 | torso angle out of range
1 | -0.07 | 1.18 | torso angle out of range
2 | -0.09 | 1.17 | torso angle out of range
3 | -0.08 | 1.17 | torso angle out of range
4 | -0.09 | 1.17 | torso angle out of range
5 | -0.08 | 1.18 | torso angle out of range
6 | -0.08 | 1.18 | torso angle out of range
7 | -0.09 | 1.17 | torso angle out of range
8 | -0.07 | 1.18 | torso angle out of range
9 | -0.07 | 1.18 | torso angle out of range

Over the 10 episodes: mean d -0.08 m, min -0.09, max -0.07; mean time survived 1.17 s; mean forward speed -0.07 m/s; episodes with d >= 3 m: 0

Episode seed 0 in detail:
joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps with |action| >= 0.99
thigh | -0.117 | 0.016 | 0.32 | 0.23
leg | -0.298 | 0.024 | 0.21 | 0.00
foot | 0.002 | 0.102 | 0.12 | 0.00
torso angle min -0.194, max 0.004 rad; torso height min 1.20, max 1.25 m
foot: on the ground 0.93 of the steps, 1 touchdowns

First 1.5 s of episode seed 0, every 0.1 s:
time (s) | x (m) | torso height (m) | torso angle (rad) | foot contact | oscillator phase(s) mod 2 pi
0.00 | 0.00 | 1.25 | -0.005 | no | 0.00
0.10 | 0.00 | 1.20 | 0.003 | yes | 1.63
0.20 | 0.05 | 1.20 | 0.000 | yes | 3.14
0.30 | 0.08 | 1.22 | -0.010 | yes | 4.78
0.40 | 0.04 | 1.24 | -0.102 | yes | 0.00
0.50 | 0.05 | 1.20 | -0.048 | yes | 1.63
0.60 | 0.06 | 1.20 | -0.037 | yes | 3.14
0.70 | 0.06 | 1.22 | -0.035 | yes | 4.78
0.80 | -0.00 | 1.23 | -0.141 | yes | 6.28
0.90 | -0.02 | 1.20 | -0.089 | yes | 1.63
1.00 | -0.02 | 1.22 | -0.069 | yes | 3.14
1.10 | -0.03 | 1.20 | -0.092 | yes | 4.78

Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):
torso_pd: 0.00
speed_lean: 0.00
thigh_hold: 0.00
thigh_swing: 0.00
leg_hold: 0.00
foot_hold: 0.00
ankle_balance: 0.00
pushoff: 0.00

## Now: round 4 of 5

Above are your earlier replies and the test results of each design, in order. Write a revised design in the same output
format (one complete spec in a single ```json code block). You may resubmit an earlier design unchanged by copying
its spec.
