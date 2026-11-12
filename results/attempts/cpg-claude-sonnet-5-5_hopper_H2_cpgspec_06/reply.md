This spec is untested, since I can't run the simulation. It uses one 2 Hz oscillator for the hop rhythm. The thigh gets a cosine swing plus torso-angle and angular-velocity feedback, and a small forward bias gives a slight lean to produce forward motion. The leg and foot compress and then extend, driven by the sine output.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1},
 "units": [
  {"type": "linear", "name": "thigh", "inputs": {"cos(hop)": 0.3, "obs[1]": -1.5, "obs[7]": -0.2},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "legfoot", "inputs": {"sin(hop)": 1.0},
   "range": 1.5, "tol": 0.05, "to": {"a1": -0.7, "a2": -0.4}}
 ]}
```