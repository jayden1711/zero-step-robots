This is an untested, hand-tuned guess: I couldn't run anything, and the joint sign conventions are assumed from MuJoCo's Hopper model.

- **Rhythm:** a single 2.5 Hz oscillator drives the knee and foot to extend in phase for push-off, and swings the thigh with a 90° offset.
- **Balance:** the torso angle and angular velocity feed back to the thigh, so a forward lean produces a positive thigh torque that pulls the torso back upright.
- **Forward speed:** a small negative thigh bias holds a slight forward lean, which is what drives forward motion.
- **Standing support:** a positive knee bias holds the leg extended against gravity.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.1, "a1": 0.3, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 2.0, "obs[7]": 0.25},
   "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "knee_push", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.2}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}}
 ]}
```