# Round 5 (final): resubmitting the round 2 design unchanged

This design is not expected to pass. It should score about 1.5 m, below the 3 m threshold. It is still the best choice, because every untested change I could make here risks dropping the score to near 0.

**What the record shows**

- **Rounds 2 and 3 are the only designs that survived.** They reached 1.50 m and 1.46 m, and both results were very consistent across seeds (spread of about 0.03 m).
- **Neither walked.** Both kept the foot planted and slowly toppled forward over it.
- **Every attempt at a real hop failed within 0.2 to 0.3 s.** That covers rounds 0, 1 and 4. In each case the thigh pinned at its 0 limit and the torso fell backward.
- **I don't have a hop design I can trust.** A working one would need the hip held off its limit while the knee drives hard enough to leave the ground, and swing timing that doesn't tip the torso. I couldn't confirm that without another test.

**Why round 2 rather than round 3**

- Round 2 had the higher mean distance (1.50 m against 1.46 m).
- Its per-seed results were as consistent as round 3's.
- Round 3 had more margin on torso angle (−0.112 against −0.167, with the limit at 0.2). But round 2 survived on all 10 seeds, and the initial perturbation on the scored seeds is the same small size.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.4, "a2": -0.06},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": -1.0, "obs[7]": -0.05},
    "range": 0.6, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_bounce",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.25},
    "range": 1.2, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "ankle_leg_angle_pd",
    "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.2, "obs[8]": 0.2, "obs[9]": 0.2},
    "threshold": -0.35, "sharpness": 6.67, "to": {"a2": 0.15}}
 ]}
```