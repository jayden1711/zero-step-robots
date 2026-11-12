## Round 4 diagnosis

- **It worked again.** All 10 episodes survived the full 8 s. d rose from 6.32 to 6.90 m, and speed from 0.79 to 0.86 m/s. Spread across seeds is still about ±0.01 m.
- **The gains are getting smaller.** The step from round 2 to 3 added 0.89 m. The step from round 3 to 4 added 0.58 m.
- **The safety margins are now thin:**
  - Torso pitch reached +0.131 rad, up from 0.112. That leaves about 0.07 rad before the 0.2 limit, and it grows with each push.
  - The foot reached -0.796 rad, which is at its -0.79 joint limit.
  - The thigh action still hits the limit on 1% of steps.

## Decision for round 5: resubmit round 4 unchanged

This design is scored without another test. Another step of the same kind would probably add about 0.4 m. If it pushes pitch past 0.2 rad, or the foot limit starts to matter, every episode could fail and the score would drop to near 0. Round 4 is tested and well past both pass criteria. Its spread across seeds is tiny, so it should behave the same on the unseen scored episodes, with a mean d of about 6.9 m.

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