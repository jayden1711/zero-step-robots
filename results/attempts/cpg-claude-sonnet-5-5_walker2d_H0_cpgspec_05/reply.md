This spec has not been run or simulated, and the joint-sign conventions are derived by hand, so treat it as an unverified attempt.

The design has three parts:
- **Posture:** a torso-angle PD term drives both hips, so a torso lean produces a restoring torque.
- **Stiffness:** PD terms hold the knees and ankles near straight.
- **Gait:** a single 1.5 Hz oscillator drives the two hips in antiphase with small amplitude. A small constant bias pushes the hips to give some forward drive.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "g", "freq_hz": 1.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.1, "a3": -0.1},
 "units": [
  {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 3.0, "obs[10]": 0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "rknee_pd", "inputs": {"obs[3]": -3.0, "obs[12]": -0.1},
   "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "lknee_pd", "inputs": {"obs[6]": -3.0, "obs[15]": -0.1},
   "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "rfoot_pd", "inputs": {"obs[4]": -2.0, "obs[13]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "lfoot_pd", "inputs": {"obs[7]": -2.0, "obs[16]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "linear", "name": "hip_swing", "inputs": {"sin(g)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a0": 0.4, "a3": -0.4}}
 ]}
```