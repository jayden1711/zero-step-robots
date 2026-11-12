Final design: this keeps the round-1 stance, which was the best so far, and adds a reflex that makes the robot step. When the thigh swings back past about -0.3 rad while the foot is planted, the knee flexes and the thigh swings forward, so the foot lands ahead of the body instead of sinking. I haven't tested this reflex.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 0.5, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
   "range": 2.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "reflex", "name": "step_knee", "inputs": {"obs[2]": -1.0}, "threshold": 0.3,
   "sharpness": 8.0, "to": {"a1": -1.5}},
  {"type": "reflex", "name": "step_thigh", "inputs": {"obs[2]": -1.0}, "threshold": 0.3,
   "sharpness": 8.0, "to": {"a0": 0.8}}
 ]}
```