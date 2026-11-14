Round 1 never walked: both feet stayed on the ground and the torso slowly tipped backward. The thigh joints are limited to angles ≤ 0, so the positive half of the thigh and balance torques only pushed on the joint limit. I couldn't test any of this, so the ankle sign is a guess from the stated conventions.

Changes in this design:
- **Ankle balance:** the feet now get torque from the torso angle and angular velocity. The sign is derived by analogy with the thigh rule you gave.
- **Forward lean:** a small constant positive thigh bias leans the torso forward.
- **Gait:** larger thigh swing and weaker knee stiffness so the legs actually step.

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
 "bias": {"a0": 0.2, "a3": 0.2, "a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.6}, "range": 1.0, "tol": 0.01, "to": {"a0": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(R)": -0.6, "obs[3]": -0.5, "obs[12]": -0.03}, "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -0.5, "obs[1]": -2.0, "obs[10]": -0.2}, "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.6}, "range": 1.0, "tol": 0.01, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(L)": -0.6, "obs[6]": -0.5, "obs[15]": -0.03}, "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -0.5, "obs[1]": -2.0, "obs[10]": -0.2}, "range": 4.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[10]": -0.4}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```