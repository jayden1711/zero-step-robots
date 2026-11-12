I can't run anything here, so this controller is an untested best guess from reasoning about the Hopper's joint sign conventions.

- **Hopping drive:** one oscillator at 2.5 Hz pushes the leg joint in a rhythmic extend/flex pattern, with a small phase-shifted thigh swing and a slight constant extension bias on the leg.
- **Torso stabilisation:** a linear unit feeds torso angle and angular velocity into the thigh torque. I assumed a forward lean gives a negative angle, so a negative thigh torque pushes the torso back upright.
- **Foot damping:** a second linear unit damps the foot joint's angle and velocity.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.2},
 "units": [
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.4},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a1": 0.7}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "foot_damp", "inputs": {"obs[4]": -0.5, "obs[10]": -0.05},
   "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```