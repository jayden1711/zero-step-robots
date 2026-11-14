This spec is untested and rests on sign conventions I couldn't check, so the controller may well fail. The two legs run antiphase oscillators at 1.5 Hz.

- **Gait:** during each leg's stance half the thigh gets a backward push. During the swing half the knee flexes, using a reflex unit.
- **Balance:** the torso angle (obs[1]) and angular velocity (obs[10]) feed both thighs. A small constant thigh bias is meant to give a slight forward lean.
- **Feet:** the feet get a spring-damper on their own joint angle and velocity.
- **Assumption:** I assumed positive torso angle means leaning backward and that negative joint torque swings a leg backward. I derived this from the joint axes and could not confirm it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "A", "freq_hz": 1.5, "phase0": 0.0},
  {"name": "B", "freq_hz": 1.5, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "A", "to": "B", "weight": 2.0, "phase_lag": 3.14159265},
  {"from": "B", "to": "A", "weight": 2.0, "phase_lag": 3.14159265}
 ],
 "bias": {"a0": 0.15, "a3": 0.15},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.5, "obs[10]": 0.2},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "thighR", "inputs": {"sin(A)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": -0.4}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(B)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a3": -0.4}},
  {"type": "reflex", "name": "kneeR", "inputs": {"sin(A)": -1.0}, "threshold": 0.2,
   "sharpness": 4.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "kneeL", "inputs": {"sin(B)": -1.0}, "threshold": 0.2,
   "sharpness": 4.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -0.8, "obs[13]": -0.05},
   "range": 1.5, "tol": 0.02, "to": {"a2": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -0.8, "obs[16]": -0.05},
   "range": 1.5, "tol": 0.02, "to": {"a5": 1.0}}
 ]}
```