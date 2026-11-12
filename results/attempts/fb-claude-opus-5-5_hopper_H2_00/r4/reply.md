# Round 4: go back to the brief's sign conventions and fix the ankle sign

## What the evidence now says

I misdiagnosed rounds 1–2. The brief's sign conventions are right, and round 3 confirms it.

- **Positive torso angle means forward lean.** In both runs where the robot fell as a nearly rigid body, x moved in the same direction as the torso angle:
  - round 0: angle −0.115, x −0.13
  - round 3: angle +0.146, x +0.16

  A rigid body pivoting on its foot moves its torso in the direction it leans, so positive is forward.
- **Negative thigh torque pitches the torso backward, as the brief says.**
  - In round 2, the torso (−0.19) and thigh (−0.235) dropped together while the leg stayed put.
  - Round 2's feedback a0 = +1.2·obs[1] was therefore positive feedback, and so was round 1's.
  - Round 0 had the correct sign but failed for a different reason. Its +0.15 bias pinned the thigh at its 0 rad limit, so the hip could not push a backward-leaning torso forward. The whole body then tipped backward slowly, and only the ankle could have stopped that.
- **Round 3's ankle loop was positive feedback.**
  - Positive foot torque raised the foot angle to +0.46, which is toe up, and the reaction pushed the shank forward.
  - So a2 = +1.2·(lean) amplified the forward fall.

## Round 4 design

**Hip (torso upright):**
- a0 = −2.5·obs[1] − 0.3·obs[7] − 0.08·obs[5] + 0.1
- The sign and structure are round 0's, with lower gains.
- The target lean is about +0.04 rad.
- The speed term reduces the lean as forward speed rises.

**Ankle (whole-body balance), sign corrected:**
- The loop acts on shank world lean, φ = obs[1] − obs[2] − obs[3], so a2 ∝ −(φ − 0.02) − 0.2·φ̇.
- It is a bounded tanh unit with output ±0.15. That limit keeps the ankle torque below what the foot can resist before the heel or toe lifts, which is what rolled the foot in round 3.
- A soft foot-joint PD adds to the same restoring direction while the foot is flat.

**Knee:**
- A PD term plus a +0.1 bias holds the knee straight.
- A 2.5 Hz sin rhythm (0.35) makes it crouch, then extend.

**Push-off and swing:**
- The foot pushes toe-down (−0.12·sin) during the knee extension.
- The thigh swings forward (−0.15·cos, small) during the flight part of the cycle.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.1},
 "units": [
   {"type": "linear", "name": "hip_torso", "inputs": {"obs[1]": -2.5, "obs[7]": -0.3, "obs[5]": -0.08},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": -0.15},
    "range": 0.2, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd", "inputs": {"obs[3]": -1.5, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_rhythm", "inputs": {"sin(cpg)": 0.35},
    "range": 0.4, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "ankle_balance",
    "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.2, "obs[8]": 0.2, "obs[9]": 0.2},
    "threshold": -0.02, "sharpness": 8.0, "to": {"a2": 0.15}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_push", "inputs": {"sin(cpg)": -0.12},
    "range": 0.15, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```

**How I'll read the result:**
- **It stays up longer than 0.9 s:** the signs are confirmed. Round 5 then scales up the hop and lean for forward speed.
- **It falls with the foot angle running away again:** the ankle sign is still wrong.
- **It falls backward with the thigh pinned at 0:** the lean target or the ankle φ* needs to shift forward.