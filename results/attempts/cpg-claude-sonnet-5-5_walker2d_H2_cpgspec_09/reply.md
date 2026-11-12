This is an untested design: two coupled phase oscillators drive the legs in antiphase, with torso-angle and angular-velocity feedback on both thighs.

- **Rhythm:** each leg's oscillator is coupled to the other with a phase lag of pi, at 1 Hz. When the leg's sine is positive the thigh is driven forward and the knee flexes (swing). When it is negative the thigh is driven back and the knee extends to support the body (stance). A small foot torque follows the same sine.
- **Balance:** both thighs get a torque of `-1.0*obs[1] - 0.1*obs[10]`. A forward lean pushes the stance thigh negative, which pitches the torso back.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.3},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.4416}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -1.0, "obs[10]": -0.1},
   "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "right_leg", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.5, "a1": -0.5, "a2": 0.2}},
  {"type": "linear", "name": "left_leg", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": 0.5, "a4": -0.5, "a5": 0.2}}
 ]}
```