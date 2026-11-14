# Round 3: a middle lean, with the ankle unit kept linear

**What round 2 showed.** With the round-0 bias and the wider ankle range, the robot survived every episode (8.00 s each). But it slowed to 0.62 m/s, so mean d was only 4.97 m, against 6.14 m in round 0.

So the 8% saturation in round 0 was not harmless. It clipped the speed-feedback term (−0.15·ẋ), which let the robot run faster than its linear setpoint. That brought both the speed (0.80 m/s) and the occasional late fall.

**Where the trade-off sits.** With the ankle unit linear (range 2.5), speed rises with the ankle bias, and the two data points are close to a straight line:

| Ankle bias | Speed | Result |
|---|---|---|
| 0.15 | 0.62 m/s | no falls |
| 0.22 | 0.99 m/s | falls at about 4.7 s (thigh folds) |

**Round 3 change.** Ankle bias 0.18, range kept at 2.5. Interpolating gives about 0.78 m/s, close to round 0's speed. If it survives all 8 s, that is about 6.2 m. Unlike round 0, the lean comes from a clean linear term rather than an accidental clip.

How I'll read the result:
- **No or very late falls:** try 0.19–0.20 next.
- **Early collapses:** the stable limit is closer to 0.15, and I fall back to the round-0 spec. It is still the best so far and can be resubmitted as the final design.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.18},
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