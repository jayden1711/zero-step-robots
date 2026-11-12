Rounds 2 and 3 both walked at about 0.9 m/s and then collapsed after roughly one gait cycle, with the torso pitched back. This revision raises the gait frequency to 1.3 Hz for shorter steps. It also adds a small forward bias at the thighs, stronger torso-angle feedback at the thighs, and restores the stronger ankle feedback from round 2. I have not run it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.3, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.3, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.2, "a4": 0.2, "a2": 0.1, "a5": 0.1},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.35, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.35, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.6, "obs[3]": -1.2, "obs[12]": -0.08},
   "range": 5.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.6, "obs[6]": -1.2, "obs[15]": -0.08},
   "range": 5.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"obs[4]": -0.3, "obs[13]": -0.03, "obs[1]": -1.5, "obs[10]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"obs[7]": -0.3, "obs[16]": -0.03, "obs[1]": -1.5, "obs[10]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```