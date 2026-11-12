Round 1 locked the leg straight: its torque bias of 0.4 pinned the leg joint at its 0 limit, so it never flexed. The thigh also drifted to about -1.17 rad with almost no torque, so the body pivoted forward over the foot until the height dropped. For round 2 I'm centring the leg torque so it can flex and extend, and adding thigh angle and angular-velocity feedback so the thigh is pulled back toward 0 and the leg stays under the torso.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.1},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -8.0, "obs[7]": -0.8, "obs[2]": -2.0, "obs[8]": -0.1},
   "range": 10.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.2}},
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": 0.2}}
 ]}
```