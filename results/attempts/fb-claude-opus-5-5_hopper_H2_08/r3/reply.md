## Round 2 diagnosis

- **The gait works.** All 10 episodes survived the full 8 s and travelled 5.43 m, at 0.68 m/s. That passes both criteria with margin. The foot was on the ground for 50% of steps, with 16 touchdowns, so it is a genuine 2 Hz hop.
- **Spread across seeds is tiny** (±0.01 m), so this gait is robust to the initial perturbation.
- **There is headroom for more speed:**
  - No unit saturated.
  - No action reached the limit; mean |action| was only 0.11–0.32.
  - The thigh only swung to -0.32 rad.
- **The main risk is torso pitch.** It reached -0.114 and +0.101 rad against a ±0.2 limit, so there is about 0.09 rad of margin.

## Changes for round 3 (moderate push for speed)

Round 2 already passes, so I'll keep it as the fallback and make only incremental changes. That way a failure can be traced and reverted.

1. **Stronger propulsion stroke:**
   - The thigh cos amplitude rises from -0.3 to -0.4, giving a longer backward sweep in stance.
   - The leg extension rises from 0.6 to 0.7, giving a slightly higher hop and a longer flight.
2. **Higher speed target:** the ankle term becomes -0.4·(obs[5] - 0.7), so the a2 bias goes from 0.2 to 0.28.
3. **Slightly stiffer torso PD** (-3.5·obs[1] - 0.45·obs[7]), to protect the pitch margin against the stronger thigh stroke. The range is widened to match.

Everything else is unchanged.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": 0.28},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -3.5, "obs[7]": -0.45},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3, "obs[5]": -0.4},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.4, "a1": 0.7, "a2": 0.3}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}}
 ]}
```