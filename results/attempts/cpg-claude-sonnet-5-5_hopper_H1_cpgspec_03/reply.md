This spec is untested, since I can't run anything here; the gains and signs are reasoned estimates.

- **Rhythm:** one 2 Hz oscillator drives the leg and foot torques from its sine and the thigh swing from its cosine. This gives the compress, push-off and swing cycle.
- **Balance:** the thigh torque gets negative feedback on torso angle and angular velocity. I assumed forward lean is positive `obs[1]` and that a positive thigh torque leans the torso forward, so the feedback gain is negative. If that sign is wrong, balance will fail.
- **Leg support:** a small constant bias on the leg joint helps hold the leg up.
- **Forward speed:** not regulated. The hop rhythm alone has to carry the robot forward.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.2, "a0": -0.05},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.12},
   "range": 1.5, "tol": 0.05, "to": {"a0": -4.0}},
  {"type": "linear", "name": "leg_push", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a1": 0.5, "a2": 0.3}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}}
 ]}
```