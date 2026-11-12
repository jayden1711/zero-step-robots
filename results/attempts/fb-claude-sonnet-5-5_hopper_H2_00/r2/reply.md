Round 1 failed because the leg stayed locked straight while the thigh swung back to -1.16 rad, so the hopper folded forward with the foot planted. In this round I add joint-angle PD terms that hold the thigh and foot near 0. I also take the oscillator off the foot and shrink its thigh swing.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": 0.5, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -3.0, "obs[8]": -0.1},
   "range": 8.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -3.0, "obs[10]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.5}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1}}
 ]}
```