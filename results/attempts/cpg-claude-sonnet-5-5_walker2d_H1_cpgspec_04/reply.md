This is a best-guess gait. I could not run it, so none of it is tested. The signs follow my reading of the Walker2d joint axes.

- **Oscillators:** the two legs run at 1 Hz and are coupled in antiphase, starting at phases 0 and pi.
- **Thighs:** each thigh gets a swing command of 0.6·sin(phase).
- **Knees:** each knee flexes hard while its thigh swings forward (about -0.8 torque) and extends gently during stance (about +0.2).
- **Balance:** both thighs get a PD term on torso angle and angular velocity, with positive gain on `obs[1]`. A forward lean (negative angle) gives a negative thigh torque, which pitches the torso back.

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
 "bias": {"a1": -0.3, "a4": -0.3},
 "units": [
  {"type": "linear", "name": "thigh_R", "inputs": {"sin(R)": 0.6},
   "range": 1.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_L", "inputs": {"sin(L)": 0.6},
   "range": 1.0, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 2.0, "tol": 0.02, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "reflex", "name": "knee_R", "inputs": {"sin(R)": 1.0},
   "threshold": 0.0, "sharpness": 5.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "knee_L", "inputs": {"sin(L)": 1.0},
   "threshold": 0.0, "sharpness": 5.0, "to": {"a4": -0.5}}
 ]}
```