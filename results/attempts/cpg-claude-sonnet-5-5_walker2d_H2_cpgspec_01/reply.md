This is an untested design, since I can't run the simulation. It has two phase oscillators locked in antiphase, one per leg. Each leg's thigh follows `-0.7*sin(phase)`, so it pushes back during stance and swings forward during swing. Each knee is a reflex that extends in stance (+0.5) and flexes in swing (-0.5). The torso-angle and angular-velocity feedback acts on both thighs, with a small forward-lean offset. The feet get stiffness and damping.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159265},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159265}
 ],
 "bias": {"a0": 0.1, "a3": 0.1},
 "units": [
  {"type": "linear", "name": "thighR_rhythm", "inputs": {"sin(R)": -0.7},
   "range": 1.2, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thighL_rhythm", "inputs": {"sin(L)": -0.7},
   "range": 1.2, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -2.0, "obs[10]": -0.3},
   "range": 3.0, "tol": 0.1, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a1": 0.5}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a4": 0.5}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```