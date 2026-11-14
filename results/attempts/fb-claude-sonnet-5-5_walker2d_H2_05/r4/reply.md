Round 3 balanced the torso (angle within about ±0.17 rad) but still sank. The thighs were saturated 64 to 80% of the time and swung back to about -1.0 rad, which splays the legs and lowers the torso until it drops below 0.8 m.

This revision replaces the open-loop thigh torque with a position-style drive. Each thigh now tracks a target angle that oscillates between about -0.65 and -0.05 rad, using angle and velocity feedback, which limits the leg splay. I reduced the torso balance gains to match. The knees, feet and oscillators are unchanged. It is untested, so the thigh spring gain is a guess.

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
 "bias": {"a0": -1.05, "a3": -1.05, "a1": 0.25, "a4": 0.25},
 "units": [
  {"type": "linear", "name": "thighR", "inputs": {"sin(R)": 0.9, "obs[2]": -3.0, "obs[11]": -0.1}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(R)": -0.5, "obs[3]": -1.0, "obs[12]": -0.04}, "range": 6.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "footR", "inputs": {"obs[4]": -0.5, "obs[1]": -2.0, "obs[10]": -0.2}, "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "thighL", "inputs": {"sin(L)": 0.9, "obs[5]": -3.0, "obs[14]": -0.1}, "range": 6.0, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(L)": -0.5, "obs[6]": -1.0, "obs[15]": -0.04}, "range": 6.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "footL", "inputs": {"obs[7]": -0.5, "obs[1]": -2.0, "obs[10]": -0.2}, "range": 4.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -2.0, "obs[10]": -0.2}, "range": 6.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}}
 ]}
```