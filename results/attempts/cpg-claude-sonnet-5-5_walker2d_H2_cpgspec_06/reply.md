This is an untested design: a two-oscillator antiphase gait with a torso-balance feedback unit. I had no way to simulate it, so the gains are reasoned guesses and may need tuning.

- **Rhythm:** two 1.2 Hz oscillators, coupled with a pi lag in both directions and started pi apart.
- **Thighs:** each is driven by its own oscillator's cosine. Positive torque swings the leg forward.
- **Knees:** each flexes (negative torque) while its thigh swings forward and extends during stance. A small positive bias keeps the knee straighter overall.
- **Balance:** one shared unit feeds torso angle and angular velocity back to both thighs with a negative sign. A +0.1 bias on the thighs gives a slight forward lean for speed.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "r", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "l", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "r", "to": "l", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "l", "to": "r", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.1, "a3": 0.1, "a1": 0.3, "a4": 0.3},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 3.0, "tol": 0.02, "to": {"a0": -1.0, "a3": -1.0}},
  {"type": "linear", "name": "thigh_r", "inputs": {"cos(r)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": 0.6}},
  {"type": "linear", "name": "thigh_l", "inputs": {"cos(l)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": 0.6}},
  {"type": "linear", "name": "knee_r", "inputs": {"cos(r)": 1.0, "sin(r)": 0.5},
   "range": 1.5, "tol": 0.02, "to": {"a1": -0.6}},
  {"type": "linear", "name": "knee_l", "inputs": {"cos(l)": 1.0, "sin(l)": 0.5},
   "range": 1.5, "tol": 0.02, "to": {"a4": -0.6}}
 ]}
```