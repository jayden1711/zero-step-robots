This is the round-0 design. Each leg has its own oscillator, and the two are coupled half a cycle apart. For each leg:

- **Thigh:** driven by `sin(phase)`, so it swings forward in the first half of the cycle and back in the second. Torso angle and angular-velocity feedback is added on top.
- **Knee:** flexes through a reflex while the leg is in its forward-swing half and extends in its stance half.
- **Feet:** unactuated for now, to keep this first design simple.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 1.5, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 1.5, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.6, "obs[1]": -0.5, "obs[10]": -0.1},
   "range": 2.5, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.6, "obs[1]": -0.5, "obs[10]": -0.1},
   "range": 2.5, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a1": -0.6}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a4": -0.6}}
 ]}
```