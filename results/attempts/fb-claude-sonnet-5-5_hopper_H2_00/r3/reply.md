Round 2 stood perfectly still: stable, but no hop and no lean. The leg sat at its straight limit (angle 0), so the positive-only leg command never crouched. This round changes three things:

- **Crouch and extend:** the leg command now swings negative as well as positive (bias 0.3, oscillator amplitude 0.6), so the leg compresses and then pushes off.
- **Forward lean:** the thigh holds a small negative angle (about -0.08 rad) via the `a0` bias, so the torso tips forward and the hops carry it in +x.
- **Rhythm:** the oscillator's cos and sin outputs now drive the leg as well as the thigh.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.25, "a1": 0.3, "a2": 0.0},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.3},
   "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -3.0, "obs[8]": -0.1},
   "range": 8.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -3.0, "obs[10]": -0.05},
   "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "height_damp", "inputs": {"obs[6]": -0.15},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "hop_sin", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.6}},
  {"type": "linear", "name": "hop_cos", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.1}}
 ]}
```