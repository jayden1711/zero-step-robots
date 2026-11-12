This is an untested design: two coupled oscillators run the legs in antiphase at 1 Hz. Each thigh gets a rhythmic swing torque plus torso-angle and angular-velocity feedback. A sine-driven reflex flexes the knee during swing and stiffens it during stance. A small PD term holds each foot flat.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "thigh_R", "inputs": {"sin(R)": 0.6, "obs[1]": -1.0, "obs[10]": -0.2},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_L", "inputs": {"sin(L)": 0.6, "obs[1]": -1.0, "obs[10]": -0.2},
   "range": 4.0, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "knee_R", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 4.0, "to": {"a1": -0.7}},
  {"type": "reflex", "name": "knee_L", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 4.0, "to": {"a4": -0.7}},
  {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```