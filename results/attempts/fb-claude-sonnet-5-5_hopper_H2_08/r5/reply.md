Round 4 is the only design that stayed upright, and it travelled about 0.93 m per episode. The three rounds before it fell backward at about 0.4 s. I can't test any further changes, so I'm resubmitting round 4 unchanged. A speculative edit could easily drop back to the earlier backward-fall behaviour. It still won't pass the 3 m threshold: the robot tips forward over its planted foot at about 0.9 s, and I couldn't work out a reliable fix without another run.

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