This is a first-guess design for round 0, so I expect to tune it from the practice results. It has one 2.5 Hz oscillator driving all three joints. The thigh gets a sin drive and the leg and foot get cos drives, so they are out of phase. A constant positive leg bias helps hold the body up. Torso angle and angular velocity feed back to the thigh with negative gain to keep the torso upright.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.3},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a0": 0.4}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3},
   "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}}
 ]}
```