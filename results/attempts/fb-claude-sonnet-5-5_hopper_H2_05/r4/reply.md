Round 3 fell because the thigh position spring (`-2*obs[2]`) pushed the torso forward once the leg swung back. The earlier rounds also show that a straight-legged vault over a planted foot always sinks and falls, so the robot has to actually hop. For round 4 I'm dropping the thigh spring and returning to the round-1 torso feedback. The knee now alternates between flexing and extending with `sin(hop)`, and the thigh swings forward while the knee is flexed, to place the foot ahead for the next landing. I haven't tested this design.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": 0.15, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5, "obs[2]": 0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "push", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": -0.25, "a1": 0.7, "a2": 0.3}}
 ]}
```