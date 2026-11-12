Round 0 fell within 0.2 s, and the logs point to the knees buckling. The knee reflex plus bias gave about -0.5 torque at start, and the right knee reached -2.39 rad. This revision keeps the knees pushed straight in stance and flexes them only briefly in swing. It also halves the thigh feedback gains so the thigh unit stops saturating. I haven't run it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"obs[1]": -1.0, "obs[10]": -0.1, "sin(R)": 0.4},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"obs[1]": -1.0, "obs[10]": -0.1, "sin(L)": 0.4},
   "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a1": -0.25}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a4": -0.25}}
 ]}
```