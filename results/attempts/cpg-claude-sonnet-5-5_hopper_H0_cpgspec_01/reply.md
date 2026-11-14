This spec is untested, since I can't run the simulation. It is a best-guess design, and the joint sign conventions below are my reading of the Hopper model, not something I checked.

- **Posture reflex:** thigh torque a0 is driven by torso angle and angular velocity, with a bias that targets a slight forward lean of about 0.05 rad. If I have the thigh sign right, this keeps the torso upright and drifts forward.
- **Hopping rhythm:** one 2.5 Hz oscillator pumps the leg joint (a1) with a sine, and adds a phase-shifted cosine to the thigh (a0). The aim is a rhythmic hop that keeps the robot moving forward.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.25},
 "units": [
  {"type": "linear", "name": "posture", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_pump", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.5}},
  {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}},
  {"type": "linear", "name": "foot_damp", "inputs": {"obs[10]": 1.0, "obs[1]": 2.0},
   "range": 12.0, "tol": 0.05, "to": {"a2": -0.1}}
 ]}
```