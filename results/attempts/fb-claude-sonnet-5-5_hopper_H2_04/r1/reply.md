Round 0 fell by height after about 1.6 s because the leg gradually collapsed, while the torso angle stayed fine. For round 1 I'm making these changes:

- **Height feedback on the leg:** the leg torque now rises as the torso height drops below about 1.25 m. The nominal leg torque is 0.4.
- **Forward lean:** a small positive thigh bias gives the torso a slight forward lean for speed.
- **Smaller rhythm amplitudes:** these are reduced so the rhythm does not buckle the leg.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 2.9},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a1": 0.4}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "height_hold", "inputs": {"obs[0]": 1.0},
   "range": 1.6, "tol": 0.02, "to": {"a1": -2.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3},
   "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}}
 ]}
```