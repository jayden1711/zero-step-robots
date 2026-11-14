This spec has not been run or simulated, so its gains are untested estimates. The sign conventions are also unverified. I assumed positive torso angle means leaning backward and positive thigh torque swings the leg forward, based on the MuJoCo joint axes.

The gait uses two oscillators at 1.2 Hz, coupled to stay half a cycle apart. During each leg's swing half of the cycle, the thigh is driven forward and the knee is flexed. The torso angle and angular velocity feed back to both thighs to keep the torso upright.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 4.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 4.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "thigh_R", "inputs": {"sin(R)": 1.0}, "range": 1.0, "tol": 0.05, "to": {"a0": 0.5}},
  {"type": "linear", "name": "thigh_L", "inputs": {"sin(L)": 1.0}, "range": 1.0, "tol": 0.05, "to": {"a3": 0.5}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15}, "range": 3.0, "tol": 0.05, "to": {"a0": 2.0, "a3": 2.0}},
  {"type": "reflex", "name": "knee_R", "inputs": {"sin(R)": 1.0}, "threshold": -0.3, "sharpness": 5.0, "to": {"a1": -0.4}},
  {"type": "reflex", "name": "knee_L", "inputs": {"sin(L)": 1.0}, "threshold": -0.3, "sharpness": 5.0, "to": {"a4": -0.4}}
 ]}
```