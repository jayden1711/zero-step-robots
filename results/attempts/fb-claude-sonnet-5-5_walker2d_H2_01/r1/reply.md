I changed the design in four ways to address the backward fall seen in round 0:

- **Balance:** the balance gain is stronger, since seed 0 pitched back to -0.855 rad.
- **Thigh rhythm:** the thigh rhythm amplitude is smaller.
- **Knee:** a positive knee bias keeps the legs extended in stance. In round 0 the knees collapsed to -2.2 and -2.7 rad.
- **Feet:** the feet now get a damped stiffness term.

I have not run it, so all values are still untested.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.4, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.4, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15},
   "range": 2.0, "tol": 0.05, "to": {"a0": -2.0, "a3": -2.0}},
  {"type": "linear", "name": "right_ankle_hold", "inputs": {"obs[4]": 1.0, "obs[12]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a2": -1.0}},
  {"type": "linear", "name": "left_ankle_hold", "inputs": {"obs[7]": 1.0, "obs[16]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```