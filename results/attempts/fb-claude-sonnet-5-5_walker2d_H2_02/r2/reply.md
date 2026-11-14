Round 1 survived about 0.9 s, but the torso pitched backward to -0.55 rad and the legs then collapsed. I'm raising the torso-feedback gains on the thighs, shrinking the rhythmic thigh swing so it disturbs the torso less, and adding a small positive thigh bias for a slight forward lean. I'm also stiffening the knees in stance. I haven't run it.

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