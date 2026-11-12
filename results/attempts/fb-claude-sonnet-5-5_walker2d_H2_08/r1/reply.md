Round 0 fell backward within 0.1 s. The balance gain on the thighs had the wrong sign: a backward lean (negative `obs[1]`) produced a negative thigh torque, which pitches the torso back further. This revision flips the balance gains to negative and lowers the rhythm amplitude.

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
 "bias": {},
 "units": [
  {"type": "linear", "name": "rightLeg", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.4, "a1": -0.4, "a2": 0.15}},
  {"type": "linear", "name": "leftLeg", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.4, "a4": -0.4, "a5": 0.15}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.13}, "range": 3.0, "tol": 0.05,
   "to": {"a0": -1.5, "a3": -1.5}}
 ]}
```