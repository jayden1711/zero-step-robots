This is a best-effort design: I can't run anything, so none of the gains have been tested. It is a single 2 Hz hop oscillator, with the thigh combining a rhythmic swing and torso balance feedback, and the leg and foot pumping in phase.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": 0.0, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "thigh", "inputs": {"obs[1]": 3.0, "obs[7]": 0.4, "cos(hop)": -0.3},
   "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg", "inputs": {"sin(hop)": 0.6},
   "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "foot", "inputs": {"sin(hop)": 0.3, "obs[1]": -1.0},
   "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```