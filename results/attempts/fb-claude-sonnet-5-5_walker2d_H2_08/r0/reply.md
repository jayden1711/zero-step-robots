This is my first-round design: two 1 Hz oscillators held in antiphase, each driving one leg, plus torso-angle feedback on both thighs. I couldn't simulate it, so the gains and the sign of the balance term are reasoned guesses, not tested values.

- **Rhythm:** the thigh torque follows `sin(phase)`, positive in swing and negative in stance. The knee torque is the opposite sign, so the knee flexes during swing. The foot gets a small torque in phase with the thigh.
- **Balance:** a forward lean (positive `obs[1]`) produces a negative thigh torque, which pitches the torso back. `obs[10]` adds damping.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "rightLeg", "inputs": {"sin(R)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a0": 0.6, "a1": -0.5, "a2": 0.2}},
  {"type": "linear", "name": "leftLeg", "inputs": {"sin(L)": 1.0}, "range": 1.2, "tol": 0.05,
   "to": {"a3": 0.6, "a4": -0.5, "a5": 0.2}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1}, "range": 3.0, "tol": 0.05,
   "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```