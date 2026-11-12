# Round 5 (final): resubmitting the round-2 design unchanged

None of the four tested designs passed. None reached 3 m in any episode. I don't expect a new, untested change to close that gap in one shot. So for the final design I'm keeping the one with the best tested score.

| Round | Mean d | Spread (min–max) | Outcome |
|---|---|---|---|
| 2 | **1.53 m** | 1.46–1.57 | fell at about 1.77 s, height too low |
| 3 | 1.48 m | 1.45–1.54 | fell at about 1.88 s, same failure |
| 4 | 0.49 m | 0.00–1.29 | mostly survived but barely moved, and inconsistent |
| 0, 1 | ≤ 0.08 m | — | no forward progress |

**Why round 2 and not a new variant:**

- **Consistency.** Round 2 has the highest mean and the tightest spread. The scored seeds differ only in a perturbation of at most 0.005, so it should score about 1.5 m again.
- **The failure isn't fixed yet.** The leg ends up trailing behind the body and the robot sinks. Rounds 3 and 4 were my two attempts to fix this. Re-timing the thigh rhythm in round 4 stopped the falls but also stopped the forward motion, and its distance varied a lot between seeds.
- **Risk.** A design halfway between round 3 and round 4 might work, but I can't test it. It could just as easily score around 0.5 m or fall early. The score is the mean distance, so keeping a reliable 1.5 m is the better expected outcome.

To be clear: this design is expected to **fail** the pass criteria (mean ≥ 3 m and at least 50 episodes ≥ 3 m), with a mean of roughly 1.5 m. With more rounds, the next thing I'd test is a partial phase shift of the thigh rhythm, between round 3 and round 4. The aim would be to bring the leg forward in flight without killing the push-off.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.25, "a1": 0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 1.0, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.25}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.45}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.4}}
 ]}
```