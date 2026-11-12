Round 0 is still the only design that moved forward. It covered 1.11 m at 0.61 m/s and kept the torso within [−0.03, 0.10] rad. Rounds 1–3 changed too much at once and either fell backward or stood still. This round goes back to round 0 and fixes only the thigh drift that ended it.

**Why round 0 drifted.** The speed term in torso balance (−3·0.03·obs[5]) pushes a0 negative as speed rises. That swings the thigh backward, so the leg trails further behind the hip. A trailing leg makes the body pitch forward and speed up, which pushes the thigh back even more. That positive feedback loop took the thigh to −1.18 rad, and the robot sank.

**Round-4 changes (relative to round 0):**
- **Speed term removed** from torso balance. Torso balance is now −3·(obs[1] + 0.15·obs[7]).
- **Thigh hold gain 0.3 → 0.6.** This is between round 0, which drifted, and round 2's 1.0, which froze the robot.
- **a0 bias 0.09 → 0.06.** With the stronger hold, the expected resting point is a thigh angle of about −0.15 rad with a forward torso lean of about 0.05 rad. That is similar to round 0's lean, so forward drive should be kept.
- **Foot hold gain 0.5 → 0.7.** The foot reached 0.62 rad in round 0, so this tames it a little.
- **Kept from round 0:**
  - 2 Hz rhythm with amplitudes −0.25 / 0.4 / 0.3.
  - Straight-leg hold.
  - No ankle speed term.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.06},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.25, "a1": 0.4, "a2": 0.3}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -0.7}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": 1.0, "obs[8]": 0.05},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.6}}
 ]}
```