This controller is untested. It uses two phase oscillators locked in antiphase, with each joint driven by a PD controller toward a target that comes from its leg's oscillator. The thighs also get torso-angle feedback.

Two assumptions in the design could be wrong, and I had no way to check them:
- **Joint axes:** I took thigh and knee angles to be at most 0, with negative values meaning the leg swings back and the knee bends.
- **Torso lean:** I took positive `obs[1]` to mean the torso leans backward. If either is wrong, the thigh and torso feedback signs flip.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "r", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "l", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "r", "to": "l", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "l", "to": "r", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.75, "a1": -0.9, "a3": -0.75, "a4": -0.9},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"obs[2]": -3.0, "obs[11]": -0.15, "sin(r)": -0.75, "obs[1]": -0.8, "obs[10]": -0.1},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"obs[3]": -3.0, "obs[12]": -0.15, "cos(r)": 0.9},
   "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"obs[4]": -2.0, "obs[13]": -0.1},
   "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"obs[5]": -3.0, "obs[14]": -0.15, "sin(l)": -0.75, "obs[1]": -0.8, "obs[10]": -0.1},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"obs[6]": -3.0, "obs[15]": -0.15, "cos(l)": 0.9},
   "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"obs[7]": -2.0, "obs[16]": -0.1},
   "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```