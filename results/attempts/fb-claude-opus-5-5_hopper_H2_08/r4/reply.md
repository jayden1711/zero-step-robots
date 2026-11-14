## Round 3 diagnosis

- **The incremental push worked.** All 10 episodes survived the full 8 s. d rose from 5.43 to 6.32 m, and speed from 0.68 to 0.79 m/s. Spread across seeds is still about ±0.01 m.
- **Torso pitch margin is unchanged.** Pitch reached -0.105 and +0.112 rad, about the same as round 2. The stiffer torso PD absorbed the stronger stroke.
- **Some limits are getting closer:**
  - The foot reached -0.74 rad against its -0.79 limit.
  - The thigh action hit the limit on 1% of steps.
  - No linear unit saturated.

## Changes for round 4 (one more step of the same kind)

Round 3 is the fallback. Round 5 can resubmit it if this round fails, so I'll take one more step in the direction that has worked twice.

1. **Stronger propulsion:**
   - Thigh cos amplitude goes from -0.4 to -0.5.
   - Leg extension goes from 0.7 to 0.8.
2. **Higher speed target:** the ankle term becomes -0.4·(obs[5] - 0.9), so the a2 bias goes from 0.28 to 0.36. The more positive foot bias also moves the foot away from its -0.79 limit.
3. **Stiffer torso PD** (-4.0·obs[1] - 0.5·obs[7]), with its range widened to 3.5, to hold the pitch margin against the stronger stroke.

Everything else is unchanged.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": 0.36},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3, "obs[5]": -0.4},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.5, "a1": 0.8, "a2": 0.3}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}}
 ]}
```