Round 2 got worse than round 1: the torso pitched backward and the robot walked in reverse, so I'm going back to the round-1 structure. From there I'm making only modest changes. The swing knee flexion and thigh drive are a bit larger so the feet actually leave the ground. The knee extension bias is slightly higher to stop the legs buckling. The angular-velocity feedback is reduced, since it was saturating the thigh actions.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.1, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.1, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.35, "a4": 0.35},
 "units": [
  {"type": "linear", "name": "r_thigh", "inputs": {"sin(R)": 0.4, "obs[1]": -1.5, "obs[10]": -0.2},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "r_knee", "inputs": {"sin(R)": -0.6},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "r_foot", "inputs": {"cos(R)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_thigh", "inputs": {"sin(L)": 0.4, "obs[1]": -1.5, "obs[10]": -0.2},
   "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "l_knee", "inputs": {"sin(L)": -0.6},
   "range": 1.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "l_foot", "inputs": {"cos(L)": 0.1, "obs[1]": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```