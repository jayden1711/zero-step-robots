This is the round-0 design: a single 2 Hz oscillator drives the leg rhythm, and a torso-balance feedback unit acts on the thigh. The sign choices are untested guesses that the practice results should correct.

- **Leg and foot:** extend together in the first half of each cycle (push-off) and flex in the second half (flight).
- **Thigh:** gets a small rhythmic swing in antiphase with the leg, so it swings forward during flight.
- **Balance:** the thigh torque opposes the torso angle (obs[1]) and angular velocity (obs[7]).

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": -0.3, "a1": 0.8, "a2": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 2.0, "tol": 0.02, "to": {"a0": 1.0}}
 ]}
```