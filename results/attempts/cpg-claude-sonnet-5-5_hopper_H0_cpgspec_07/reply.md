I can't run anything here, so this controller is untested and is my best reasoning about the Hopper's dynamics, not a verified gait. It has two parts:

- **Balance:** a linear unit on torso angle, angular velocity and forward speed drives the foot and thigh. A positive torso angle (forward lean) gives a positive foot torque that pushes the torso back. A forward-speed term and a constant negative foot bias tilt it forward so it keeps moving.
- **Hopping:** one 2.5 Hz oscillator drives the leg and thigh torques to produce periodic hops.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a2": -0.1},
 "units": [
  {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3, "obs[5]": 0.3},
   "range": 9.0, "tol": 0.05, "to": {"a2": 1.0, "a0": 0.4}},
  {"type": "linear", "name": "leg_pulse", "inputs": {"sin(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.4}}
 ]}
```