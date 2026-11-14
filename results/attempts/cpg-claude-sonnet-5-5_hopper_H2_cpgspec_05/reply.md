This spec is untested, since I can't run anything here. It combines a 2 Hz hop rhythm, balance feedback on the thigh, and a small constant forward lean.

- **Rhythm:** one oscillator at 2 Hz drives the leg joint with `sin` (compress, then extend), the thigh with `cos` (swing forward in flight), and the foot with a small `sin`.
- **Balance:** the thigh gets `-3*obs[1] - 0.3*obs[7]`. This opposes the torso angle and angular velocity, so a forward lean produces a negative thigh torque that pitches the torso back.
- **Speed:** a small positive thigh bias of 0.1 leans the torso slightly forward to produce forward motion.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1},
 "units": [
   {"type": "linear", "name": "balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3},
    "range": 4.0, "tol": 0.05, "to": {"a0": -1.0}},
   {"type": "linear", "name": "leg_push", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.05, "to": {"a1": 0.5, "a2": 0.2}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.05, "to": {"a0": 0.3}}
 ]}
```