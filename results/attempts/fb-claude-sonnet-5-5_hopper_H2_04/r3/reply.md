Round 3 goes back to the round 0 layout, which was the only design that hopped and balanced the torso. I made three changes to address how it failed, which was a slow forward runaway ending in a leg collapse.

- **Speed feedback:** the thigh gets a term on forward speed (obs[5]) so the torso pitches back as speed builds.
- **Angular-velocity gain:** the gain on torso angular velocity is raised from 0.3 to 0.4.
- **Leg height feedback:** a mild height term on the leg torque, calibrated so the leg torque is unchanged at a height of 1.25 m. It stiffens the leg as the torso sinks.

I'm also dropping the round 1 and 2 leg setups, which locked the leg straight. The thigh rhythm is trimmed from 0.4 to 0.3, since a rhythmic thigh torque with the foot planted pitches the torso.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 1.3},
 "units": [
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a1": 0.6}},
  {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.1, "tol": 0.02, "to": {"a2": 0.3}},
  {"type": "linear", "name": "height_hold", "inputs": {"obs[0]": 1.0},
   "range": 1.6, "tol": 0.02, "to": {"a1": -0.8}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.4, "obs[5]": 0.5},
   "range": 6.0, "tol": 0.05, "to": {"a0": -1.0}}
 ]}
```