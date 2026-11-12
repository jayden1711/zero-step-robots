Round 2 stayed upright but fell forward over a planted foot. The thigh drifted to about -1.2 rad, the leg stayed straight, and the torso sagged below 0.7 m. This revision adds a thigh PD term that pulls the thigh back toward about -0.1 rad, so the foot gets brought under the body instead of trailing. The rest is as in round 2, with the thigh rhythm trimmed.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.3, "a1": 5.3, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 0.2, "sin(hop)": 0.1},
   "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 0.3},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(hop)": 0.2, "cos(hop)": 0.1},
   "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "height_spring", "inputs": {"obs[0]": -4.0},
   "range": 6.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -3.0, "obs[8]": -0.05},
   "range": 9.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
   "range": 5.0, "tol": 0.05, "to": {"a0": -5.0}}
 ]}
```