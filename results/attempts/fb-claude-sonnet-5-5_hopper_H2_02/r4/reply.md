Round 3 stayed upright but toppled forward: the torso angle stayed near 0 while the thigh slowly folded back to about -1.2 rad, so the body fell over the foot. This revision adds thigh-angle feedback to resist that fold, and slightly increases the leg's rhythmic push so there is more hopping motion. If it does worse than round 3, I'll go back to the round 3 design.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": 0.1},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.4},
   "range": 2.5, "tol": 0.05, "to": {"a0": -3.0}},
  {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
   "range": 3.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}},
  {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.4}},
  {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a2": 0.1}}
 ]}
```