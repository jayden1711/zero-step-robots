This spec is untested: I couldn't run it, and I assumed the sign conventions for torso angle and joint torques. The design is two oscillators held in antiphase at 1.5 Hz.

- **Thighs:** each thigh is driven by `0.6*sin(phase)`. The positive half of the cycle is swing, the negative half is stance.
- **Knees:** each knee flexes during its leg's swing via a reflex unit on `sin(phase)`.
- **Balance:** a PD term on the torso angle and angular velocity is added to both thighs.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.5, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.5, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 5.0, "phase_lag": 3.14159265},
  {"from": "L", "to": "R", "weight": 5.0, "phase_lag": 3.14159265}
 ],
 "bias": {"a1": -0.2, "a4": -0.2},
 "units": [
  {"type": "linear", "name": "thigh_R", "inputs": {"sin(R)": 1.0}, "range": 1.0, "tol": 0.05, "to": {"a0": 0.6}},
  {"type": "linear", "name": "thigh_L", "inputs": {"sin(L)": 1.0}, "range": 1.0, "tol": 0.05, "to": {"a3": 0.6}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15}, "range": 1.5, "tol": 0.05, "to": {"a0": 2.0, "a3": 2.0}},
  {"type": "reflex", "name": "knee_R", "inputs": {"sin(R)": 1.0}, "threshold": 0.2, "sharpness": 5.0, "to": {"a1": -0.2}},
  {"type": "reflex", "name": "knee_L", "inputs": {"sin(L)": 1.0}, "threshold": 0.2, "sharpness": 5.0, "to": {"a4": -0.2}}
 ]}
```