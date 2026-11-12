This is an untested design, since I can't run the simulation.

**Design**
- **Oscillators:** two at 1.2 Hz, held in antiphase by mutual coupling with a lag of pi.
- **Thighs:** each thigh gets a swing torque from its own oscillator's sin.
- **Knees:** each knee flexes through a reflex while its oscillator's sin is positive (swing) and is extended otherwise (stance).
- **Balance:** the torso angle and angular velocity feed back to both thighs, with a small bias that holds a slight forward lean.
- **Feet:** a damped stiffness term keeps each foot flat.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "r", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "l", "freq_hz": 1.2, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "r", "to": "l", "weight": 2.0, "phase_lag": 3.14159265},
  {"from": "l", "to": "r", "weight": 2.0, "phase_lag": 3.14159265}
 ],
 "bias": {"a0": -0.2, "a3": -0.2, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 2.0, "obs[10]": 0.3},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "thigh_r", "inputs": {"sin(r)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.5}},
  {"type": "linear", "name": "thigh_l", "inputs": {"sin(l)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": 0.5}},
  {"type": "reflex", "name": "knee_r", "inputs": {"sin(r)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a1": -0.4}},
  {"type": "reflex", "name": "knee_l", "inputs": {"sin(l)": 1.0}, "threshold": 0.0,
   "sharpness": 5.0, "to": {"a4": -0.4}},
  {"type": "linear", "name": "foot_r", "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
   "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "foot_l", "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
   "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```