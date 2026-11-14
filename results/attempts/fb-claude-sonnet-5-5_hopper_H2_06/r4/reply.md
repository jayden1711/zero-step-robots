Round 4 is another reasoned guess. Rounds 2 and 3 were consistent: a negative foot torque when the torso tilts back survived slightly longer than a positive one. The positive-foot design failed fastest, at 0.20 s. So I'm keeping the round-2 structure and making the foot feedback much stronger. I'm also adding a small constant negative foot bias so the torso settles into a slight forward lean instead of falling backward. The leg bias and foot rhythm stay removed.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a2": -0.15},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -10.0, "obs[7]": -1.0},
   "range": 8.0, "tol": 0.02, "to": {"a0": 0.5, "a2": -1.0}}
 ]}
```