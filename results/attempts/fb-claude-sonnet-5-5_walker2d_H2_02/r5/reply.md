Round 2 was the best result so far (mean d 0.66 m, versus 0.25 m in round 4 and negative in round 3). I can't test changes before this final submission, and my last two edits made things worse. So I'm resubmitting the round-2 design unchanged rather than gambling on an untested tweak.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.1, "a3": 0.1, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3, "sin(R)": 0.25},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3, "sin(L)": 0.25},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a1": -0.4}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.3,
   "sharpness": 4.0, "to": {"a4": -0.4}}
 ]}
```