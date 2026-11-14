Round 1 was the best so far, but the thigh drifted back to -1.2 rad and the torso sank until it fell. Round 2 failed because its thigh set point was positive, past the 0 limit, which pinned the thigh and tipped the torso forward.

For round 3 I'm adding a weak thigh spring toward a rearward set point of -0.25 rad, which is inside the joint limit. I'm keeping the round-1 torso-angle feedback and the always-positive leg torque, with a modest leg and foot pulse.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.5, "a1": 0.5, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5, "obs[2]": 2.0, "obs[8]": 0.1},
   "range": 4.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "push", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a1": 0.3, "a2": 0.2}}
 ]}
```