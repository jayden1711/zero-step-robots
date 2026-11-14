Round 3 moved forward (0.87 m) and kept the torso near upright, but the robot sank until the height check failed. The thighs swung back to about -1.2 rad, and the ankles saturated at their limit, probably from the torso-angle feedback I added to them. This revision stiffens the knees so the stance legs hold the body up, and cuts the ankle share of the balance feedback from 0.5 to 0.2.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "r", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "l", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "r", "to": "l", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "l", "to": "r", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[10]": -0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0, "a2": 0.2, "a5": 0.2}},
  {"type": "linear", "name": "thigh_r", "inputs": {"sin(r)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a0": 0.3}},
  {"type": "linear", "name": "thigh_l", "inputs": {"sin(l)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a3": 0.3}},
  {"type": "linear", "name": "knee_r", "inputs": {"obs[3]": -2.5, "obs[12]": -0.2, "sin(r)": -0.6},
   "range": 8.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "knee_l", "inputs": {"obs[6]": -2.5, "obs[15]": -0.2, "sin(l)": -0.6},
   "range": 8.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "foot_r", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 0.5}},
  {"type": "linear", "name": "foot_l", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 0.5}}
 ]}
```