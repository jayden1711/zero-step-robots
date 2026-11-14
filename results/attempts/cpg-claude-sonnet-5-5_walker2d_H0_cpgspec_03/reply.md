This spec is untested, since I can't run anything here. It combines one oscillator driving the thighs in antiphase, knee flexion during swing, and PD stabilisation of the torso, knees and ankles. The signs of the hip and torso feedback are my best guess from the joint axis conventions and may be wrong.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "p", "freq_hz": 1.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.1, "a4": 0.1},
 "units": [
  {"type": "linear", "name": "hip_drive", "inputs": {"sin(p)": 1.0}, "range": 1.2, "tol": 0.02, "to": {"a0": 0.4, "a3": -0.4}},
  {"type": "reflex", "name": "r_swing_knee", "inputs": {"cos(p)": 1.0}, "threshold": 0.3, "sharpness": 5.0, "to": {"a1": -0.3}},
  {"type": "reflex", "name": "l_swing_knee", "inputs": {"cos(p)": -1.0}, "threshold": 0.3, "sharpness": 5.0, "to": {"a4": -0.3}},
  {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 2.0, "obs[10]": 0.3}, "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "r_knee_pd", "inputs": {"obs[3]": -1.0, "obs[12]": -0.1}, "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee_pd", "inputs": {"obs[6]": -1.0, "obs[15]": -0.1}, "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_ankle_pd", "inputs": {"obs[4]": -1.0, "obs[13]": -0.1}, "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_ankle_pd", "inputs": {"obs[7]": -1.0, "obs[16]": -0.1}, "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```