# Round 1: flip the balance sign and fix the bias offsets

## What went wrong in round 0

The robot fell backward within 6 steps. The cause was a positive-feedback loop:

1. Both thighs started with large negative torque. That came from the -0.6 biases, and since sin φ = 0 at the start, nothing offset them.
2. That negative torque pitched the torso backward, to obs[1] < 0.
3. My balance term (+2·obs[1]) then made the thigh torque more negative still.
4. Both thighs saturated at -1, and the torso passed -1 rad almost immediately.

The data confirms what the task statement says: negative thigh torque pitches the torso backward. So my round-0 sign argument was wrong. The balance feedback must **oppose** the signs of obs[1] and obs[10], as the hint said.

The knee biases were also inconsistent. A -0.5 bias contradicted the "straight in stance" target.

## Changes for round 1

- **Balance feedback flipped**, and the gains lowered:
  - -1.5·obs[1] - 0.2·obs[10] per thigh.
  - Both thighs carry it, so the total is about 3 and 0.4.
  - A small positive bias (0.075) adds a slight forward lean, a torso target of about +0.05 rad.
- **Thigh target is now 0.3·sin φ**, centred on zero, with no large offset bias. Swing is when cos φ > 0.
- **Knees:**
  - Proportional-derivative control towards 0 rad, with gain 1.5 and damping 0.15, and no bias.
  - A reflex adds -0.8 during swing (cos φ > 0.3) and about +0.8 during stance, which locks the knee straight.
- **Feet:** hold at 0 rad, unchanged.
- **Oscillators:** unchanged, 0.9 Hz in antiphase.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.075, "a3": 0.075},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.6, "obs[2]": -2.0, "obs[11]": -0.2, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.3, "sharpness": 4.0,
    "to": {"a1": -0.8}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.6, "obs[5]": -2.0, "obs[14]": -0.2, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.3, "sharpness": 4.0,
    "to": {"a4": -0.8}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```