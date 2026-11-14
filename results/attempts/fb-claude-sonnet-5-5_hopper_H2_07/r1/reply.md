Round 0 hopped forward (about 0.92 m/s) but sank until the torso fell below 0.7 m at about 1 s. For round 1 I'm making the leg stiffer, with a higher extension bias and a smaller compression swing. I'm also shrinking the thigh and foot rhythm amplitudes so they disturb the torso less, and raising the balance gains slightly.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.5},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.15}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.15}}
 ]}
```