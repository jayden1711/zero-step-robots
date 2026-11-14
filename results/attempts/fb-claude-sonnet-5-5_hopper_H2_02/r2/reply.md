Both runs fell backward at about 0.3 to 0.4 s while the thigh stayed pinned near its 0 rad joint limit. That limit means a positive thigh torque can't pitch the torso forward. This revision gives the thigh a small negative bias so it sits off the limit and the balance feedback has authority. It also cuts the leg and foot oscillation so stance compression doesn't throw the torso back, and raises the angular-velocity damping.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.15, "a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.4},
   "range": 2.5, "tol": 0.05, "to": {"a0": -1.5}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.05}},
  {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.15}},
  {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a2": 0.1}}
 ]}
```