This spec is untested, since I can't run anything here. It sets a 2 Hz oscillator that drives a leg-extension pulse once per hop, with posture feedback on the thigh. The signs and gains come from my reading of the Hopper joint axes, not from simulation.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 0.1},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "swing", "inputs": {"cos(hop)": 0.3},
   "range": 1.5, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_push", "inputs": {"sin(hop)": 0.8},
   "range": 1.5, "tol": 0.02, "to": {"a1": 1.0}},
  {"type": "linear", "name": "foot_push", "inputs": {"sin(hop)": 0.4},
   "range": 1.5, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```