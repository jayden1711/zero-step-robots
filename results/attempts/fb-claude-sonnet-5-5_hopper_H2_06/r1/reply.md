The round-0 hopper fell backward within 0.27 s, before the first push-off finished. The thigh rhythm (-0.3 at phase 0) was pitching the torso back, and the balance gain was too weak to counter it. This revision flips the thigh rhythm to a small forward drive, removes most of the leg extension while the leg is already straight, and strengthens the balance feedback.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.5, "a2": 0.2}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0}}
 ]}
```