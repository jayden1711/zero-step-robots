This revision targets the knee collapse seen in round 0. The knees reached about -2.7 rad, so the robot sank and tipped backward until the height check failed. Each knee now has a PD hold toward straight, with the swing flexion from the oscillator added on top. I also reduced the thigh swing amplitude and kept the torso feedback and foot damping.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "r", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "l", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "r", "to": "l", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "l", "to": "r", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -2.0, "obs[10]": -0.2},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "thigh_r", "inputs": {"sin(r)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a0": 0.4}},
  {"type": "linear", "name": "thigh_l", "inputs": {"sin(l)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a3": 0.4}},
  {"type": "linear", "name": "knee_r", "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(r)": -0.6},
   "range": 6.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "knee_l", "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(l)": -0.6},
   "range": 6.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "foot_r", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a2": 0.5}},
  {"type": "linear", "name": "foot_l", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 2.0, "tol": 0.05, "to": {"a5": 0.5}}
 ]}
```