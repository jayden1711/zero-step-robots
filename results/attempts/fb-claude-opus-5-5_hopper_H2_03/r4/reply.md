# Round 4: stiffen the thigh to stop the late collapses, at round-3 speed

**What round 3 showed.** Ankle bias 0.18 gave the best result so far: mean d 6.33 m at 0.89 m/s, and all 10 episodes passed. But 6 of the 10 episodes fell between 6.1 s and 7.2 s, mostly with "height too low". In every round so far:

- d is almost exactly speed × time survived (0.89 × 7.20 ≈ 6.4; 0.62 × 8.00 ≈ 5.0).
- So round 3 at its current speed, surviving all 8 s, would reach about 7.1 m.
- The late falls therefore cost about 0.7 m, which is now the main thing to win back.

**What causes the falls.** It is the failure we saw clearly in round 1. The thigh folds back (to −1.14 rad there), the leg ends up behind the body, and the torso sinks below 0.7 m. The only thing pulling the thigh back toward vertical is `thigh_spring`, and it is weak (0.3 per rad). At −0.6 rad it gives only about 0.15 of torque.

**Round 4 change (only one).** I'm making the thigh spring stiffer and better damped:

| | Stiffness on q2 | Damping on q̇2 |
|---|---|---|
| Before | −0.3 | −0.03 |
| Now | −0.5 | −0.05 |

- The a0 bias goes from −0.03 to −0.05. This keeps the spring's rest angle at −0.1 rad, so the nominal posture doesn't change.
- I widened the unit's range to 1.5 so it stays linear even if the thigh reaches about −1.1 rad.
- The ankle bias stays at 0.18 and everything else matches round 3. Any change in results comes from the thigh spring alone.

**How I'll use the result for the final design (round 5):**
- **Falls drop and speed stays around 0.85 m/s or more:** keep this design, possibly with the ankle bias nudged to 0.185.
- **Speed drops a lot, or new torso-angle falls appear:** the stiffer hip is fighting the torso loop. I'll resubmit round 3 unchanged, since it is the best verified design (6.33 m).

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.05, "a1": -0.5, "a2": 0.18},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```