This spec is untested, since I can't run anything. It combines posture stabilisation with a simple alternating gait from one oscillator, and the signs and gains are a best guess.

- **Torso:** a PD unit on torso angle and angular velocity drives both hips.
- **Feet:** each ankle gets a PD unit that keeps the foot flat.
- **Hips:** the oscillator drives them in antiphase.
- **Knees:** a reflex on the oscillator flexes each knee during its swing and extends it during stance.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "g", "freq_hz": 1.2, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.5, "obs[10]": 0.15},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "r_foot_pd", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 3.0, "tol": 0.02, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot_pd", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 3.0, "tol": 0.02, "to": {"a5": 1.0}},
  {"type": "linear", "name": "hip_cpg", "inputs": {"sin(g)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.4, "a3": -0.4}},
  {"type": "reflex", "name": "r_knee_swing", "inputs": {"cos(g)": 1.0},
   "threshold": 0.3, "sharpness": 4.0, "to": {"a1": -0.5}},
  {"type": "reflex", "name": "l_knee_swing", "inputs": {"cos(g)": -1.0},
   "threshold": 0.3, "sharpness": 4.0, "to": {"a4": -0.5}}
 ]}
```