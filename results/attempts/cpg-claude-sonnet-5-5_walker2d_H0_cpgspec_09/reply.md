This is an untested best guess: a single oscillator drives antiphase hip swing, with feedback loops for balance. I could not run anything, so there is no guarantee it reaches 3 m.

- **Torso balance:** the hips get a torque from torso angle and angular velocity, pushing the legs under the torso when it leans forward.
- **Joint stiffness:** the knees and feet are PD-held toward straight.
- **Gait:** the oscillator swings the thighs in antiphase and bends the knee of the swing leg.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "g", "freq_hz": 1.5, "phase0": 0.5, "feedback": {}}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -3.0, "obs[10]": -0.3},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "linear", "name": "hip_swing", "inputs": {"sin(g)": 1.0},
   "range": 1.5, "tol": 0.05, "to": {"a0": 0.3, "a3": -0.3}},
  {"type": "linear", "name": "r_knee_hold", "inputs": {"obs[3]": -2.0, "obs[12]": -0.1},
   "range": 5.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "l_knee_hold", "inputs": {"obs[6]": -2.0, "obs[15]": -0.1},
   "range": 5.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "r_foot_hold", "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
   "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "l_foot_hold", "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
   "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "reflex", "name": "r_knee_swing", "inputs": {"sin(g)": 1.0}, "threshold": 0.0,
   "sharpness": 6.0, "to": {"a1": -0.2}},
  {"type": "reflex", "name": "l_knee_swing", "inputs": {"sin(g)": -1.0}, "threshold": 0.0,
   "sharpness": 6.0, "to": {"a4": -0.2}}
 ]}
```