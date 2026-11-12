This controller is a best guess, since I can't run anything to check it. The signs of the joint torques and the hop timing are untested.

- **Balance:** the thigh torque is a PD feedback on torso angle, with a small forward-lean setpoint of about 0.05 rad to encourage forward drift.
- **Hop:** one 2 Hz oscillator drives the leg joint around a positive bias to pump the leg and hop.
- **Foot:** a small foot torque follows the oscillator to help push-off.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15, "a1": 0.4},
 "units": [
  {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -3.0, "obs[7]": -0.5},
   "range": 6.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_pump", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "foot_push", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a2": 0.2}}
 ]}
```