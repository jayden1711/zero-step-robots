This is an untested first-guess controller, since I can't run anything here.

- **Rhythm:** one 2 Hz oscillator drives the hop cycle. The leg joint follows sin(phase), the thigh follows cos(phase), and the foot follows sin(phase) at lower amplitude.
- **Balance:** the thigh torque is -3 × (obs[1] + 0.1 × obs[7]). This opposes the torso angle and angular velocity.
- **Forward speed:** a thigh bias of +0.12 holds the torso slightly forward (about 0.04 rad), so the hopper drifts ahead.
- **Leg bias:** a small leg bias of +0.15 keeps the leg a little extended.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.12, "a1": 0.15},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.1},
   "range": 1.3, "tol": 0.05, "to": {"a0": -3.0}},
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a0": 0.3}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a1": 0.7}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.05, "to": {"a2": 0.3}}
 ]}
```