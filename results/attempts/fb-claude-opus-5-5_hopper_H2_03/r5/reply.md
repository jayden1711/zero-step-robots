# Round 5 (final): resubmit the round-3 design unchanged

**What round 4 showed.** The stiffer thigh spring made things worse.
- Mean d fell from 6.33 m to 5.41 m.
- Mean survival fell from 7.20 s to 5.90 s.
- Every episode fell, and 9 of the 10 falls were "torso angle out of range" rather than "height too low".
- Speed barely changed (0.92 vs 0.89 m/s).

This is the second outcome I named in round 4. With the foot planted, extra hip torque reacts directly onto the torso, so a stiffer thigh spring fights the torso loop and pitches the torso out of range. My idea that a weak hip spring caused the late collapses was wrong, or at least that fix doesn't work.

**Why not try something new in the final round.** Any change now would be scored without being tested. The options I could see either look unlikely to help or are too small to rely on:
- A softer spring with a slightly higher ankle bias.
- An ankle bias of 0.17.

Round 3 is the best design I have actually tested:
- Mean d was 6.33 m.
- All 10 practice episodes passed with a wide margin (minimum 5.69 m against the 3 m threshold).
- Its falls all came late, after 6 s, so they cost little distance.

The scored seeds differ only by tiny initial perturbations, so I expect a score of about 6.3 m that comfortably passes. Some seeds will still fall in the last 1–2 s.

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