Round 0 passed comfortably: every practice episode reached d ≥ 3 m, with mean d 6.14 m at about 0.8 m/s. The late falls (around 6.7–7.4 s) still scored 5.9–6.9 m, so speed matters more to the score than these falls. Round 1 makes two small changes and keeps everything else the same, so the effect of each is easy to read:

1. **Push for more speed.** The ankle bias `a2` goes from 0.15 to 0.22. This leans the reference posture further forward, which raises the speed the controller settles at.
2. **Stop the ankle unit saturating.** `ankle_balance_speed` was saturated on 8% of steps, so I widened its declared range from 1.5 to 2.5. It now stays linear through the transients instead of clipping its feedback.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.22},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.3, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

How I'll read the next results:
- **Speed rises and falls stay rare:** I'll push the ankle bias further or increase the knee amplitude.
- **Falls increase:** I'll go back to bias 0.15 and work on torso damping instead.