Round 1 shows the leg locked straight (leg angle about 0) while the thigh angle drifted to about -1.2 rad. The thigh had almost no torque (mean |action| 0.03), so the foot slid backward and the torso sank. For round 2 I'm adding thigh angle and velocity feedback to hold the thigh near vertical. I'm also adding a small thigh bias so the torso settles at a slight forward lean and drifts forward.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 0.5},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4, "obs[2]": 2.0, "obs[8]": 0.2},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.15}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.15}}
 ]}
```