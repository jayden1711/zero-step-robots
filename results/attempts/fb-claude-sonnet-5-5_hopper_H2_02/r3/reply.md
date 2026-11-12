Round 2 was the first design to stay up for more than about 0.4 s. The leg stayed locked straight, but the torso drifted backward and the thigh slowly folded. This revision removes the negative thigh bias that caused the backward lean, and raises the balance gain. It also lets the leg compress slightly on part of each cycle, so there is some hopping motion rather than pure standing.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": 0.15},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.4},
   "range": 2.5, "tol": 0.05, "to": {"a0": -3.0}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}},
  {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.3}},
  {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a2": 0.1}}
 ]}
```