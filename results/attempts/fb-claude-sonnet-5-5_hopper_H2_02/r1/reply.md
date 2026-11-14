Round 0 fell backward after about 0.3 s. The thigh torque was saturated 28% of the time, and the oscillating thigh term plus the high balance gain pitched the torso back. For this revision I'm lowering the balance gain, adding damping through the angular-velocity term, shrinking the thigh swing, and reducing the leg and foot push.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 0.2},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
   "range": 2.5, "tol": 0.05, "to": {"a0": -2.0}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}},
  {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.5}},
  {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a2": 0.2}}
 ]}
```