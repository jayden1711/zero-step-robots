Round 3 fell backward more slowly but still fell, and it made no forward progress. The thighs were saturated against their straight-leg joint limit (thigh angle near 0), so extra thigh gain did little. This revision adds torso feedback at the ankles, since a positive ankle torque with the foot planted also pitches the torso forward. It also returns the thigh gains and rhythm amplitude to moderate values, and drops the foot-angle PD. The gains are still untested guesses.

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
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.25, "a4": 0.25},
 "units": [
  {"type": "linear", "name": "rightThigh", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.3}},
  {"type": "linear", "name": "leftThigh", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.3}},
  {"type": "reflex", "name": "rightKnee", "inputs": {"sin(R)": 1.0}, "threshold": 0.2,
   "sharpness": 5.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "leftKnee", "inputs": {"sin(L)": 1.0}, "threshold": 0.2,
   "sharpness": 5.0, "to": {"a4": -0.5}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15}, "range": 4.0, "tol": 0.05,
   "to": {"a0": -2.0, "a3": -2.0, "a2": -1.5, "a5": -1.5}}
 ]}
```