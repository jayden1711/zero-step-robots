This is an untested first-pass design, so I can't say whether it clears the 3 m threshold.

- **Rhythm:** two oscillators at 1 Hz, coupled both ways with a lag of pi so they settle in antiphase. Each thigh gets `0.7*cos(phase)`: forward swing when positive, backward stance push when negative. Each knee gets `0.6*sin(phase)`: flexed in early swing, extended late in swing and early in stance.
- **Balance:** both thighs get `-1.5*obs[1] - 0.3*obs[10]`, which pushes back against forward lean and forward pitch rate. A thigh bias of +0.15 sets a lean of about 0.1 rad at equilibrium, which should give some forward drive.
- **Feet:** a mild PD on each ankle keeps the foot from flopping.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "A", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "B", "freq_hz": 1.0, "phase0": 3.14159265}
 ],
 "couplings": [
  {"from": "A", "to": "B", "weight": 2.0, "phase_lag": 3.14159265},
  {"from": "B", "to": "A", "weight": 2.0, "phase_lag": 3.14159265}
 ],
 "bias": {"a0": 0.15, "a3": 0.15},
 "units": [
  {"type": "linear", "name": "thigh_R", "inputs": {"cos(A)": 0.7, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_L", "inputs": {"cos(B)": 0.7, "obs[1]": -1.5, "obs[10]": -0.3},
   "range": 6.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "knee_R", "inputs": {"sin(A)": 0.6},
   "range": 1.0, "tol": 0.02, "to": {"a1": 1.0}},
  {"type": "linear", "name": "knee_L", "inputs": {"sin(B)": 0.6},
   "range": 1.0, "tol": 0.02, "to": {"a4": 1.0}},
  {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[11]": -0.05},
   "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.05},
   "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```