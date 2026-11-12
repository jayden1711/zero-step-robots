I could not run or test anything, so this is an untested hand-built design. It has three parts:

- **Balance:** the ankle torque (a2) is driven by torso pitch and pitch rate, with a small negative bias so the hopper rests with a slight forward lean.
- **Hop drive:** one 2 Hz oscillator pumps the knee (a1) and swings the hip (a0) with a phase offset to produce a hopping rhythm.
- **Hip damping:** a weak hip term on torso angular velocity.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a2": -0.15},
 "units": [
  {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
   "range": 3.0, "tol": 0.02, "to": {"a2": 1.0}},
  {"type": "linear", "name": "knee_pump", "inputs": {"sin(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a1": 0.5}},
  {"type": "linear", "name": "hip_swing", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.3}},
  {"type": "linear", "name": "hip_damp", "inputs": {"obs[7]": 0.1},
   "range": 10.0, "tol": 0.02, "to": {"a0": 1.0}}
 ]}
```