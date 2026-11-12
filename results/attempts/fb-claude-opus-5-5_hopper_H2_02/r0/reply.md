Round 0 is a conservative first design. The goal is to stay healthy for the full 1000 steps and drift forward, and to learn the phase signs from the test results.

**Structure**
- **One oscillator** at 2 Hz sets the hop rhythm.
- **Leg joint (a1)**: a PD controller holds the leg straight, and a rhythm term `0.4·cos(hop)` adds compression and push-off.
- **Foot (a2)**: a PD controller holds the foot near 0, plus a small rhythm term (`0.2·cos(hop)`).
- **Thigh (a0)**: a rhythm term `0.3·sin(hop)`, a quarter cycle out of phase with the leg, swings the leg in flight.
- **Balance on the thigh**: `−4·obs[1] − 0.5·obs[7]`, which opposes torso lean and its rate.
  - A bias of +0.15 on a0 sets a small forward-lean target (about 0.04 rad) to drive forward motion.
  - A small `−0.1·obs[5]` term reduces that lean as forward speed rises, which regulates speed.

The balance unit is linear up to |z| = 2, beyond which it saturates. That covers the action limit with margin.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.15},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.4},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.2},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```