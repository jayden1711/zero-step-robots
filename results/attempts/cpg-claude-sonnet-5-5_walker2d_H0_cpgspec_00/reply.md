This controller is untested, as the task requires, so it is a best-guess gait. It uses one oscillator that drives the two legs in antiphase, with an ankle reflex to hold the torso upright.

- **Hips:** the right and left thigh torques are `±0.6·sin(phase)`, opposite in sign, so one thigh swings forward while the other is pushed onto its extension stop.
- **Knees:** the knee of whichever leg is swinging gets a strong flexion torque to clear the ground, and the stance knee stays lightly flexed.
- **Ankles:** both feet get a torque proportional to torso angle and angular velocity. The sign assumes that a forward lean is a positive angle.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "g", "freq_hz": 1.6, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": -0.5, "a4": -0.5},
 "units": [
  {"type": "linear", "name": "hip", "inputs": {"sin(g)": 1.0}, "range": 1.2, "tol": 0.01,
   "to": {"a0": 0.6, "a3": -0.6}},
  {"type": "reflex", "name": "knee", "inputs": {"sin(g)": 1.0}, "threshold": 0.0, "sharpness": 5.0,
   "to": {"a1": 0.5, "a4": -0.5}},
  {"type": "linear", "name": "ankle", "inputs": {"obs[1]": 1.5, "obs[10]": 0.15}, "range": 3.0, "tol": 0.02,
   "to": {"a2": 1.0, "a5": 1.0}}
 ]}
```