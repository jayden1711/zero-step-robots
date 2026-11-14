This is my round-0 design: two antiphase oscillators drive the legs, with torso-angle feedback on both thighs. It is untested, since I can't run it.

- **Gait:** each leg's oscillator is coupled to the other with a half-cycle lag, and runs at 1 Hz.
- **Thigh:** driven by `sin(phase)`, so it swings forward when sin is positive and back when negative.
- **Knee:** flexes during swing and is extended during stance, with a small constant bias toward straight for support.
- **Foot:** gets a small ankle command in phase with the thigh.
- **Balance:** a shared linear unit feeds the torso angle and angular velocity to both thighs with negative gains.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a1": 0.2, "a4": 0.2},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.5}, "range": 1.0, "tol": 0.01, "to": {"a0": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(R)": -0.5, "cos(R)": -0.2}, "range": 1.0, "tol": 0.01, "to": {"a1": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"sin(R)": 0.2}, "range": 1.0, "tol": 0.01, "to": {"a2": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.5}, "range": 1.0, "tol": 0.01, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(L)": -0.5, "cos(L)": -0.2}, "range": 1.0, "tol": 0.01, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"sin(L)": 0.2}, "range": 1.0, "tol": 0.01, "to": {"a5": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -1.0, "obs[10]": -0.15}, "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```