This spec is untested, since I can't run the simulation. It uses one 2 Hz oscillator, and the numbers are my best estimates.

- **Balance:** the thigh torque is `-6*obs[1] - 0.8*obs[7]`, which opposes torso lean and spin. A constant thigh bias of +0.25 keeps a slight forward lean to drive forward speed.
- **Rhythm:** the leg torque follows `0.6*sin(phase)` to compress and extend. The foot follows `0.3*sin(phase)`, and the thigh swing follows `0.3*cos(phase)`.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.25},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -6.0, "obs[7]": -0.8},
   "range": 10.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_push", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.6, "a2": 0.3}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```