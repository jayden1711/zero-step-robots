Round 1 pitched backward and drifted back about 1 m in every episode. Likely cause: the thigh limit at 0 wastes the positive half of the thigh rhythm, so the rhythm nets out as a backward push on the torso.

This revision makes four changes, still untested:
- **Thigh rhythm:** amplitude reduced from 0.4 to 0.25.
- **Thigh bias:** +0.25 on both thighs, to pitch the torso forward.
- **Balance:** feedback gain on torso angle and angular velocity raised.
- **Knee:** the swing flexion is kept the same.

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
 "bias": {"a0": 0.25, "a3": 0.25, "a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.25, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.25, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 2.0, "tol": 0.05, "to": {"a0": -3.0, "a3": -3.0}},
  {"type": "linear", "name": "right_ankle_hold", "inputs": {"obs[4]": 1.0, "obs[12]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a2": -1.0}},
  {"type": "linear", "name": "left_ankle_hold", "inputs": {"obs[7]": 1.0, "obs[16]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```