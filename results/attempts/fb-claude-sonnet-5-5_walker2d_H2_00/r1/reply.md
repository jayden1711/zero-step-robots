Round 0 fell backward within 0.5 s. The stance leg's negative thigh torque (the swing-phase half of the cosine) pitched the torso back, and the balance feedback was too weak to counter it. This revision halves the rhythmic thigh amplitude, raises the balance gains roughly threefold, adds a small forward-torque bias on both thighs, and softens the knee and foot drives.

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
 "bias": {"a0": 0.1, "a3": 0.1},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"cos(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "thighL", "inputs": {"cos(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a3": 0.3}},
  {"type": "reflex", "name": "kneeR", "inputs": {"cos(R)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a1": -0.3}},
  {"type": "reflex", "name": "kneeL", "inputs": {"cos(L)": 1.0}, "threshold": 0.0, "sharpness": 4.0, "to": {"a4": -0.3}},
  {"type": "linear", "name": "footR", "inputs": {"sin(R)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a2": 0.1}},
  {"type": "linear", "name": "footL", "inputs": {"sin(L)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a5": 0.1}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```