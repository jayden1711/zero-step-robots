This is an untested design. Two oscillators run in antiphase at 1.2 Hz and drive the thighs and knees. Torso-angle and angular-velocity feedback is added to both thighs, with a small bias toward a slight forward lean. The feet get a simple joint-angle PD hold.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.2, "a3": 0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"cos(R)": 0.6, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 6.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"cos(L)": 0.6, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 6.0, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"cos(R)": -0.35, "sin(R)": 0.35},
   "range": 1.0, "tol": 0.02, "to": {"a1": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"cos(L)": -0.35, "sin(L)": 0.35},
   "range": 1.0, "tol": 0.02, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 3.0, "tol": 0.02, "to": {"a2": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 3.0, "tol": 0.02, "to": {"a5": 1.0}}
 ]}
```