This is the final round and none of the five earlier designs passed. The best distance was about 0.94 m, in rounds 0 and 1. For round 5 I'm taking the round-2 design, which held the thigh near vertical and stayed up longest in height terms. I'm removing the thigh bias and halving the thigh-angle feedback, because those two pushed the torso forward until it tipped. I'm also raising the torso-angle gain, and I'm keeping the stiff round-1 leg with a small compression swing. I haven't tested this combination, so it's a gamble.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.5},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5, "obs[2]": 1.0, "obs[8]": 0.1},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.15}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1}}
 ]}
```