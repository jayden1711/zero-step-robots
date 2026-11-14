This is my round-0 design: a single 2 Hz oscillator drives a hop rhythm, with balance feedback on the thigh. I haven't been able to test it, so the gains are initial guesses.

- **Rhythm:** The leg joint gets `0.7*sin(phase) + 0.3` bias, so it alternates between pushing off and flexing around a mostly extended leg. The thigh swings with `0.3*cos(phase)`, and the foot follows with `0.2*sin(phase)`.
- **Balance:** The thigh gets `-5*obs[1] - 0.5*obs[7]`. This follows the hint's sign convention: a forward lean produces a negative thigh torque, which pitches the torso back.
- **Forward drive:** A small positive thigh bias of 0.05 adds a slight forward lean.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a1": 0.7, "a2": 0.2}},
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.2, "tol": 0.02, "to": {"a0": 0.3}}
 ]}
```