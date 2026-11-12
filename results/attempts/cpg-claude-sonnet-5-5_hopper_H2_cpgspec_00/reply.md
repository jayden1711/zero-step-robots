I haven't run or tested this, so the gait parameters are an educated guess rather than a tuned result. The design is one 2 Hz oscillator giving a hop cycle of about 62 steps.

- **Leg and foot:** the leg and foot torques follow cos(phase), so they extend together for push-off and flex together in flight.
- **Thigh rhythm:** the thigh gets a sin(phase) component, a quarter cycle out of phase with the leg, to swing the leg forward in flight.
- **Balance:** the thigh gets feedback from torso angle and angular velocity, both with negative sign. A forward lean produces a negative hip torque, which pitches the torso back.
- **Forward lean:** a small negative bias on the thigh keeps a slight forward-driving lean.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.05},
 "units": [
  {"type": "linear", "name": "leg_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a1": 0.8, "a2": 0.3}},
  {"type": "linear", "name": "thigh_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a0": -0.4}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}}
 ]}
```