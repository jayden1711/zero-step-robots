This spec is untested and can't be validated here, so treat it as a first attempt. It uses two coupled oscillators locked in antiphase. Each oscillator drives its leg's thigh with a sine and flexes the knee during swing. Torso angle and angular velocity feed back to both thighs. I assumed a thigh torque of the opposite sign to a forward lean pulls the torso upright, which I couldn't check.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "units": [
  {"type": "linear", "name": "thigh_R", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1, "sin(R)": 0.5},
   "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "thigh_L", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1, "sin(L)": 0.5},
   "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "knee_R", "inputs": {"sin(R)": -1.0, "cos(R)": 0.3}, "threshold": 0.0,
   "sharpness": 4.0, "to": {"a1": -0.8}},
  {"type": "reflex", "name": "knee_L", "inputs": {"sin(L)": -1.0, "cos(L)": 0.3}, "threshold": 0.0,
   "sharpness": 4.0, "to": {"a4": -0.8}}
 ]}
```