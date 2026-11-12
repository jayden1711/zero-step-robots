Round 0 fell at about 0.8 s with the torso pitching backward, and both knees collapsed. This revision lowers the rhythmic amplitudes, doubles the torso-angle feedback on the thighs, and adds knee and ankle stiffness plus a small extension bias on the knees.

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
 "bias": {"a1": 0.15, "a4": 0.15},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.35, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.35, "obs[1]": -2.0, "obs[10]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.4, "obs[3]": -0.8, "obs[12]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.4, "obs[6]": -0.8, "obs[15]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"obs[4]": -0.5, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"obs[7]": -0.5, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```