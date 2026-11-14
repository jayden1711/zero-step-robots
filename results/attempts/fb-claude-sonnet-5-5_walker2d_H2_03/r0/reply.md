This is my round-0 design: two antiphase oscillators at 1.2 Hz drive each leg's thigh, knee and foot, and torso-angle and angular-velocity feedback is added to both thighs. I haven't been able to test it, so the gains are initial guesses to revise from the practice results.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.6, "obs[1]": -0.8, "obs[10]": -0.2},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.7},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.3, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.6, "obs[1]": -0.8, "obs[10]": -0.2},
   "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.7},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.3, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```