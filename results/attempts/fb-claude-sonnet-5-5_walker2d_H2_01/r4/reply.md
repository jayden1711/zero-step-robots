Round 3 was the first design to make forward progress, and the ankle feedback was the main help. This revision targets the two problems it left: the knees collapsing (left leg reached -1.97 rad) and the ankle torque saturating on 41% of steps. The changes are untested.

- **Knee stiffness:** a spring-damper on each knee resists flexion.
- **Knee rhythm:** more knee bias with a smaller swing amplitude.
- **Ankle balance:** gain lowered from 3 to 2.

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
 "bias": {"a0": 0.25, "a3": 0.25, "a1": 0.35, "a4": 0.35, "a2": 0.15, "a5": 0.15},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.25, "a1": 0.45}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.25, "a4": 0.45}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 2.0, "tol": 0.05, "to": {"a0": -2.0, "a3": -2.0}},
  {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 2.0, "tol": 0.05, "to": {"a2": -2.0, "a5": -2.0}},
  {"type": "linear", "name": "right_knee_stiff", "inputs": {"obs[3]": 1.0, "obs[12]": 0.1},
   "range": 3.0, "tol": 0.05, "to": {"a1": -1.5}},
  {"type": "linear", "name": "left_knee_stiff", "inputs": {"obs[6]": 1.0, "obs[15]": 0.1},
   "range": 3.0, "tol": 0.05, "to": {"a4": -1.5}}
 ]}
```