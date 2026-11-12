This is a blind best guess: I could not simulate it, and the sign conventions for the joints are my reading of the Walker2d model, so treat it as untested.

- **Rhythm:** two oscillators at 1.5 Hz, coupled in antiphase and started half a cycle apart.
- **Thighs:** each follows `0.6*sin(phase)`, so it swings forward in swing and back in stance.
- **Knees:** each flexes during swing and extends during stance through a reflex on `sin(phase)`.
- **Balance:** a PD term on torso angle (`obs[1]`) and angular velocity (`obs[10]`) feeds both thigh torques.
- **Not included:** I added no ankle drive and no explicit forward-lean speed regulation.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.5, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.5, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159265},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159265}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.5, "a3": 1.5}},
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.6}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": 0.6}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(R)": 1.0}, "threshold": 0.2,
   "sharpness": 3.0, "to": {"a1": -0.3}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(L)": 1.0}, "threshold": 0.2,
   "sharpness": 3.0, "to": {"a4": -0.3}}
 ]}
```