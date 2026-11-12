The torso fell backward at about 0.4 s in every round, the same moment the leg torque goes negative (rhythm phase past pi). That torque flexes the knee, which I think is what tips the torso back. This revision keeps the leg torque positive throughout by adding a bias, so the knee stays mostly extended. It also restores the round-1 thigh feedback with a stronger forward-lean bias, and uses a small positive foot feedback and a weak rhythmic foot push. I can't confirm any of this without a run.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.3, "a1": 0.5},
 "units": [
  {"type": "linear", "name": "thigh_balance_swing", "inputs": {"obs[1]": -8.0, "obs[7]": -0.8, "cos(hop)": 0.1},
   "range": 12.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_push", "inputs": {"sin(hop)": 0.4},
   "range": 1.0, "tol": 0.01, "to": {"a1": 1.0}},
  {"type": "linear", "name": "foot_balance", "inputs": {"obs[1]": 2.0, "obs[7]": 0.2, "cos(hop)": 0.1},
   "range": 6.0, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```