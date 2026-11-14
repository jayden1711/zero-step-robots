This is my round-0 design. It uses one 2.5 Hz oscillator for the hop rhythm, with torso-angle and angular-velocity feedback on the thigh. The gains are initial guesses that I expect to revise after the practice results.

- **Balance:** the thigh torque is `-(3*obs[1] + 0.3*obs[7])`. A forward lean gives a negative thigh torque, which pitches the torso backward.
- **Leg:** `0.3 + 0.7*sin(phase)`, so it compresses in the negative half-cycle and extends (pushes off) in the positive half.
- **Foot:** `0.3*sin(phase)`, in phase with the leg.
- **Thigh rhythm:** `0.3*cos(phase)`, a quarter-cycle ahead of the leg, to swing the leg forward in flight.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.7, "a2": 0.3}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```