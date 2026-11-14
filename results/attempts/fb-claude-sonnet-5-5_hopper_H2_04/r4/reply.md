Round 4 keeps the round 0 and round 3 layout and changes four things, based on how round 3 failed:

- **Speed feedback:** the gain on obs[5] is cut from 0.5 to 0.15. Round 3 pitched the torso backward too hard and fell over backward in several episodes.
- **Torso-angle and angular-velocity feedback:** both are raised, since round 2 showed the torso tipping forward when the feedback was weak.
- **Leg height feedback:** the slope is increased so the leg stiffens faster as the torso sinks. The leg torque at a height of 1.25 m is unchanged.
- **Thigh restoring term:** a mild term pulls the thigh back toward 0, so the leg does not trail far behind the torso as it did in rounds 0 and 3, where the thigh reached about -1.2.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 1.8},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "height_hold", "inputs": {"obs[0]": 1.0},
   "range": 1.6, "tol": 0.02, "to": {"a1": -1.2}},
  {"type": "linear", "name": "thigh_restore", "inputs": {"obs[2]": 1.0},
   "range": 2.7, "tol": 0.02, "to": {"a0": -0.5}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.5, "obs[5]": 0.15},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}}
 ]}
```