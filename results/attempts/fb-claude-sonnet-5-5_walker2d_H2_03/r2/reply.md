Round 1 survived about 1.4 s but barely moved forward (0.5 m in 1.4 s), and the legs buckled at the end. For round 2 I'm raising the knee extension bias and swing flexion, and adding a small forward thigh bias to produce forward lean and push. I'm also reducing the torso feedback gains, since the thigh actions were saturating 38% of the time.

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
 "bias": {"a0": 0.1, "a3": 0.1, "a1": 0.4, "a4": 0.4},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.4, "obs[1]": -1.0, "obs[10]": -0.15},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.5},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.4, "obs[1]": -1.0, "obs[10]": -0.15},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.5},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```