This spec is untested, since I can't run anything here. It combines a torso-angle balance reflex with a 2.5 Hz hopping rhythm.

- **Balance:** the thigh and foot torques oppose torso lean and its angular velocity. The signs are my best reading of the Hopper joint axes, so they could be wrong.
- **Hopping:** one oscillator drives the leg joint, with a phase-shifted hip swing to push the robot forward.
- **Forward speed:** a small forward-velocity term on the hip tries to keep a steady lean in the direction of travel.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.1},
   "range": 2.0, "tol": 0.02, "to": {"a0": -3.0, "a2": -2.0}},
  {"type": "linear", "name": "leg_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "hip_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "speed_hold", "inputs": {"obs[5]": 0.1},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.2}}
 ]}
```