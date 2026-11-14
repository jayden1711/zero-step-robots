Round 0 pitched the torso backward within 0.2 s, so the robot fell with the torso at about -0.5 rad. My guess is that the swing/stance thigh torque (0.6) was too large and the knees flexed to their limit (about -2.7 rad). For this revision I'm reducing the thigh and knee amplitudes, adding a constant extension bias to both knees, strengthening the torso feedback, and slowing the gait to 1.0 Hz.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.3, "a4": 0.3},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.3, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.4},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.3, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.4},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```