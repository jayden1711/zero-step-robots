This is the final round and I can't simulate, so this is a modest revision of round 4, which was the most stable. Round 4 ended in a height collapse, with the thigh drifting back to about -1.15 rad while the torso stayed upright. I'm pulling the thigh back toward 0 harder, and I'm raising the torso feedback so that doesn't tip the body forward, as it did in round 2.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15, "a1": 1.8},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "height_hold", "inputs": {"obs[0]": 1.0},
   "range": 1.6, "tol": 0.02, "to": {"a1": -1.2}},
  {"type": "linear", "name": "thigh_restore", "inputs": {"obs[2]": 1.0},
   "range": 2.7, "tol": 0.02, "to": {"a0": -1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.6, "obs[5]": 0.15},
   "range": 10.0, "tol": 0.05, "to": {"a0": -1.0}}
 ]}
```