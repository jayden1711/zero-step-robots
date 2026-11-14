This is an untested design: a single 2 Hz oscillator drives the hop, and the thigh gets balance feedback.

- **Rhythm:** the leg torque follows `sin(phase)`, so the leg compresses and then extends. The foot follows the same signal at lower gain. The thigh gets a `cos(phase)` swing, 90° out of phase with the leg.
- **Balance:** the thigh torque is `-3*obs[1] - 0.4*obs[7]`, which opposes the torso angle and its angular velocity.
- **Speed:** a `-0.15*obs[5]` term on the same unit lowers the thigh torque when forward speed is high. A constant bias of `+0.1` on the thigh adds a small forward lean.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": -0.2},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4, "obs[5]": -0.15},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a1": 0.8, "a2": 0.3}},
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": 0.4}}
 ]}
```