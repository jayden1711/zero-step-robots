# Round 3 design

## What round 2 showed

Round 2 was the first design with a working balance loop. The robot survived 2.7 s and moved forward at about 0.56 m/s. It then slowly sank until it hit the height limit.

The cause was the robot slowly falling forward over its foot:

- **Height drifted down steadily.** It went 1.25 → 1.20 → 1.15 → 1.10 m over the first 1.4 s, then down to 0.70 m.
- **The thigh angle drifted to −1.06 rad.** The hip kept the torso upright while the leg tipped further and further forward. That made the hip fold and the torso drop.
- **The foot reached its joint limit (−0.82 rad).** The leg tipped so far that the foot joint was pinned.
- **The ankle was too weak to stop the tilt.** Its output was capped at ±0.15, which is only about ±30 Nm, plus the −0.06 bias. Its gain was only about 1 per radian of leg tilt.

## Round 3 changes

| Joint | Change |
|---|---|
| **Ankle (a2)** | Cap raised from 0.15 to 0.35, and gain raised to about 1.75 per radian of leg tilt. I added forward-speed feedback (−0.3·obs[5]). When the robot speeds up, the ankle pushes the top of the leg back, and this works before the tilt has built up. The threshold moves to −0.47, which keeps the same posture (leg tipped forward 0.35 rad) at a target speed of about 0.4 m/s. That speed gives about 3.2 m over 8 s. Leg-rate damping is unchanged relative to the angle term. |
| **Hip (a0)** | Slightly stiffer: −1.5·obs[1] − 0.08·obs[7]. The torso reached −0.167 rad early in round 2, close to the 0.2 limit. The damping is still well below the level that went unstable in rounds 0–1. |
| **Knee (a1)** | Unchanged. It provides the 2.5 Hz bounce that produced the forward progress. |

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.4, "a2": -0.06},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": -1.5, "obs[7]": -0.08},
    "range": 0.8, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_bounce",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.25},
    "range": 1.2, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "ankle_leg_angle_speed",
    "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.2, "obs[8]": 0.2, "obs[9]": 0.2, "obs[5]": -0.3},
    "threshold": -0.47, "sharpness": 5.0, "to": {"a2": 0.35}}
 ]}
```