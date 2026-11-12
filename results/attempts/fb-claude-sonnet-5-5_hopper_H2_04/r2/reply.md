Round 1 never hopped. The leg stayed locked straight, with leg torque saturated 12% of the time, and the whole body tipped forward over the planted foot until the height fell below 0.7 m. For round 2 I'm making these changes:

- **Leg:** the large constant torque is replaced by a moderate bias plus a mild height feedback, so the leg can flex and extend and the robot actually hops.
- **Thigh restoring term:** a new term pushes the thigh back toward 0 when it drifts negative, so the leg is not left trailing behind the torso.
- **Balance gain:** the torso-angle gain is lowered so the balance feedback does not keep driving the thigh negative.
- **Thigh swing:** the rhythmic swing is slightly larger, to bring the leg forward in flight.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 1.65},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a0": 0.5}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "height_hold", "inputs": {"obs[0]": 1.0},
   "range": 1.6, "tol": 0.02, "to": {"a1": -1.0}},
  {"type": "linear", "name": "thigh_restore", "inputs": {"obs[2]": 1.0},
   "range": 2.7, "tol": 0.02, "to": {"a0": -1.5}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 2.0, "obs[7]": 0.3},
   "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}}
 ]}
```