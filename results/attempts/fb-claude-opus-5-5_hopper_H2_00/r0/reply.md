Round 0 is a conservative baseline. It balances the torso through the hip, holds the leg and foot with simple joint stiffness, and adds a moderate 2 Hz hop rhythm. The point is to learn whether the robot stays upright before pushing for speed.

- **Torso balance (to a0):** a0 = −4·obs[1] − 0.5·obs[7] − 0.15·obs[5] + 0.15. The bias sets a small forward lean (about 0.04 rad). The speed term reduces that lean as forward speed rises, which regulates speed.
- **Leg and foot stiffness:** a joint-angle and joint-velocity controller holds each joint near straight (0 rad), so the leg acts like a spring.
- **Rhythm:** one 2 Hz oscillator drives the leg joint (sin, amplitude 0.5), the foot (sin, 0.2) and the thigh (cos, 0.3). The thigh swing therefore runs a quarter cycle ahead of the leg push.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.15},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(cpg)": 0.5},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(cpg)": 0.2},
    "range": 0.3, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```