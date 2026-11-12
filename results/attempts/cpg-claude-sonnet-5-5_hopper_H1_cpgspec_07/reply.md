This spec is untested, since I can't run anything here. It's a best-guess hopping controller with a single 2 Hz oscillator driving the three joints, plus torso-angle feedback on the thigh. The feedback signs and phase relationships come from my reading of the Hopper joint conventions and may need tuning.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.2},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": 0.3, "a1": 0.8, "a2": 0.3}},
  {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": -0.4}}
 ]}
```