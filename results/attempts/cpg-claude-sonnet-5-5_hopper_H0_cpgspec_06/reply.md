This spec is untested, since I can't run anything here. It combines three ideas.

- **Balance:** the thigh torque follows the torso angle and angular velocity (a0 = 5·obs[1] + 0.8·obs[7]), assuming a positive torso angle means leaning back.
- **Forward lean:** a small constant thigh bias (0.15) tilts the torso forward.
- **Hopping:** a 2.5 Hz oscillator pulses the leg and foot torques to drive forward hops.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.8},
   "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_pulse", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.5, "a2": -0.3}},
  {"type": "linear", "name": "swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}}
 ]}
```