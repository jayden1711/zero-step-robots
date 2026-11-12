Round 2 stood on a locked-straight leg and tipped forward, so it never hopped. Round 0 was the only design that hopped, though it sank and let the thigh drift back to about -1.3 rad. For round 3 I'm going back to the round-0 leg drive (0.3 bias, 0.7 swing) so the leg compresses and pushes off again. I'm keeping the thigh angle and velocity feedback from round 2 to stop that drift. The thigh bias drops from 0.2 to 0.1 to reduce the forward-tipping torque seen in round 2.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4, "obs[2]": 2.0, "obs[8]": 0.2},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.7, "a2": 0.3}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```