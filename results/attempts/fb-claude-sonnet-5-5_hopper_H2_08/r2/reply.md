The torso still falls backward at about 0.4 s. In the logs the thigh angle sits at 0, which is its joint limit, so extra thigh feedback torque can't pitch the torso forward. This revision adds the same upright feedback at the foot joint, whose reaction also pitches the torso forward when the foot is planted. It also halves the leg push to reduce the deep compression.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1},
 "units": [
  {"type": "linear", "name": "thigh_balance_swing", "inputs": {"obs[1]": -8.0, "obs[7]": -0.8, "cos(hop)": 0.15},
   "range": 12.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_push", "inputs": {"sin(hop)": 0.3},
   "range": 1.0, "tol": 0.01, "to": {"a1": 1.0}},
  {"type": "linear", "name": "foot_balance", "inputs": {"obs[1]": -10.0, "obs[7]": -1.0, "cos(hop)": 0.2},
   "range": 6.0, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```