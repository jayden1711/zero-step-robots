This is an untested design: two antiphase leg oscillators at 1 Hz, with torso-angle and torso-angular-velocity feedback on both thighs.

- **Rhythm:** the right leg is at phase 0 and the left at phase pi, and mutual coupling with a pi lag holds them half a cycle apart.
- **Swing and stance:** during swing (sin > 0) the thigh torque is positive and the knee torque is negative, so the leg flexes and moves forward. During stance (sin < 0) the thigh torque is negative, pushing the body forward, and the knee extends to support it.
- **Balance:** both thighs get `-1.0*obs[1] - 0.2*obs[10]`. This opposes a forward lean, and a stance thigh with negative torque pitches the torso back.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159265},
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159265}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -1.0, "obs[10]": -0.2},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "right_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.5, "tol": 0.05, "to": {"a0": 0.6, "a1": -0.5}},
  {"type": "linear", "name": "left_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.5, "tol": 0.05, "to": {"a3": 0.6, "a4": -0.5}}
 ]}
```