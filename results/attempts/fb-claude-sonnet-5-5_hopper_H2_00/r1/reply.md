Round 0 failed because the leg collapsed: the torso height sank from 1.25 m to 0.71 m, while the torso angle stayed within limits. For round 1 I'm making the leg stiffer. That means a higher constant leg-extension bias, a smaller oscillator swing, and a damping term that extends the leg when the torso is moving down.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.6, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1, "a1": 0.4, "a2": 0.2}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.2}}
 ]}
```