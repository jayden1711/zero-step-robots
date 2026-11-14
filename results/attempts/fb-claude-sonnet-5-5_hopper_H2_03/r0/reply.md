This is my round-0 design: a single 2 Hz oscillator drives the hop rhythm, with torso-angle and angular-velocity feedback on the thigh. It is untested, and the gains are my best estimates.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
   "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
   "range": 1.2, "tol": 0.05, "to": {"a1": 0.5, "a2": -0.2}},
  {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.2, "tol": 0.05, "to": {"a0": 0.3}}
 ]}
```

The thigh balance term opposes torso lean and spin, with a small positive thigh bias so the torso settles at a slight forward lean. The leg gets a bias plus a sine drive for compress-and-extend, and the foot counter-drives lightly.