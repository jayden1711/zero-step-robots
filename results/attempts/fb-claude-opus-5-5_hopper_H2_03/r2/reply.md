# Round 2: back to the round-0 lean, keeping the wider ankle range

**What round 1 showed.** Speed rose (0.80 → 0.99 m/s), but survival fell sharply: mean time survived went from 7.74 s to 4.73 s, and mean d dropped from 6.14 m to 4.63 m. Most falls were "height too low". In seed 0 the thigh folded to −1.14 rad (−0.65 in round 0) and the torso dropped to 0.71 m. The extra forward lean is more than the hip loop can hold. The robot ends up running under itself until the thigh collapses.

**A problem with my round-1 test.** I said I would change things so each effect was easy to read, but I changed two things at once: the ankle bias and the ankle unit's range. So I can't yet say how much of the drop came from the bias and how much from the range.

**Round 2 separates them.** I'm putting the ankle bias back to 0.15 (the round-0 value) and keeping the wider 2.5 range. Everything else matches round 0, so this is a single-variable comparison against round 0:
- **Results close to round 0 (~6.1 m, rare falls):** the bias caused the collapse and the wider range is harmless or helps. Next I'll look for speed through the push-off instead of more lean.
- **Results worse than round 0:** the saturating range was acting as a useful limit on the ankle's authority, and I'll go back to the exact round-0 spec as the base.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.15},
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