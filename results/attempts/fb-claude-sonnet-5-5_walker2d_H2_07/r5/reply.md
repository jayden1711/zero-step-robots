This is the final design. Rounds 3 and 4 moved forward but fell after about 1.2 s with the thighs swinging back to about -1.2 rad. So I replaced the open-loop thigh swing with a stiff joint-angle hold around a slightly back-swung angle, with a smaller oscillator swing on top. I also removed the torso feedback to the ankles and strengthened the foot damping, since the feet kept saturating at about 0.8 rad. I have not run this design, so I don't know whether it will reach 3 m.

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
 "bias": {"a0": -0.3, "a3": -0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "thigh_r", "inputs": {"obs[2]": -1.0, "obs[11]": -0.08, "sin(r)": 0.4},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_l", "inputs": {"obs[5]": -1.0, "obs[14]": -0.08, "sin(l)": 0.4},
   "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "knee_r", "inputs": {"obs[3]": -2.5, "obs[12]": -0.2, "sin(r)": -0.6},
   "range": 8.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "knee_l", "inputs": {"obs[6]": -2.5, "obs[15]": -0.2, "sin(l)": -0.6},
   "range": 8.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "foot_r", "inputs": {"obs[4]": -1.5, "obs[13]": -0.1},
   "range": 4.0, "tol": 0.05, "to": {"a2": 0.7}},
  {"type": "linear", "name": "foot_l", "inputs": {"obs[7]": -1.5, "obs[16]": -0.1},
   "range": 4.0, "tol": 0.05, "to": {"a5": 0.7}}
 ]}
```