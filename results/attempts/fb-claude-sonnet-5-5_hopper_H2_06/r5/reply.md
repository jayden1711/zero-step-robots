This is my final design. It is an untested guess, since the earlier rounds only showed that the hopper falls backward within about 0.3 s.

In every round the thigh angle stayed pinned at its 0 rad limit (round 4: -0.005 to 0.004 rad). With the thigh locked straight, thigh torque is internal to the rigid torso-and-leg chain, so the balance feedback had no authority. This revision adds a constant negative thigh bias and a negative leg bias. They bend the hip and knee into a slight crouch, so a positive balance torque can pitch the torso forward. I dropped the foot feedback and foot bias, because both signs made things no better.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.3, "a1": -0.2},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -10.0, "obs[7]": -1.0},
   "range": 8.0, "tol": 0.02, "to": {"a0": 1.0}}
 ]}
```