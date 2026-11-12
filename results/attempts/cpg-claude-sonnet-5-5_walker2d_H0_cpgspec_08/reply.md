This is an untested, hand-derived controller, so I can't say whether it reaches 3 m. The signs rest on my reading of the Walker2d joint conventions (positive torso angle means leaning backward, positive thigh angle swings the leg forward), which I couldn't check. If that is wrong, the hip balance term will destabilise the walker.

The design has four parts:
- **Hip balance:** a PD term on torso angle, with a small forward-lean target.
- **Joint damping:** knees are held near straight and the ankles are damped.
- **Gait:** one 1.2 Hz oscillator swings the thighs in antiphase.
- **Swing-phase knee flexion:** a reflex bends the swing knee.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "g", "freq_hz": 1.2, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a3": 0.1},
 "units": [
  {"type": "linear", "name": "hip_balance", "inputs": {"obs[1]": -2.0, "obs[10]": -0.3},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "knee_r", "inputs": {"obs[3]": -1.0, "obs[12]": -0.05},
   "range": 6.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "knee_l", "inputs": {"obs[6]": -1.0, "obs[15]": -0.05},
   "range": 6.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "ankle_r", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
   "range": 6.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "ankle_l", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
   "range": 6.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "linear", "name": "gait_swing", "inputs": {"sin(g)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.4, "a3": -0.4}},
  {"type": "reflex", "name": "knee_flex", "inputs": {"cos(g)": 1.0}, "threshold": 0.0,
   "sharpness": 3.0, "to": {"a1": -0.3, "a4": 0.3}}
 ]}
```