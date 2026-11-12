Round 0 failed two ways. The leg torque swung negative for half of each cycle, so the knee collapsed (the "height too low" falls). The thigh bias and swing probably contributed to the backward torso falls. For round 1 I'm keeping the leg torque always positive (extending), cutting the thigh bias and swing to near zero, and keeping the same balance feedback to see whether the robot stays up.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 0.5, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
   "range": 2.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "push", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a1": 0.4, "a2": 0.3}},
  {"type": "linear", "name": "swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": 0.1}}
 ]}
```