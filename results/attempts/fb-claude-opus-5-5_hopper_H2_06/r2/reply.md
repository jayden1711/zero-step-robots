# Round 2 design

## What went wrong in rounds 0–1

The −0.19 rad torso angle in round 0 was not a static geometry match. It was the last value before the episode ended at the 0.2 limit, so my round-1 explanation was incomplete. Three things together explain both rounds:

1. **The hip joint was pinned.** The thigh angle stayed at 0, which is its upper limit. When the torso fell backward, the feedback asked for positive thigh torque, but that only pushed into the limit. The hip therefore had no effect on the torso in either round.

2. **The ankle bias pushed the robot backward.** With the foot on the ground, negative foot torque tips the leg's top backward. Round 1's ankle bias of −0.15 did exactly that: the foot angle went to −0.215 and the torso fell back.

3. **The gains were far too high.** The actuators are strong (gear 200, so 0.1 of action is about 20 Nm). A torso damping of 0.3 gives a discrete-time loop gain above 2 at 0.008 s per step, which makes the loop unstable. Round 0's thigh torque was saturated on 33% of steps, which fits that.

**Geometry constraint.** The hip and knee can only swing the lower part backward. So to keep the hip off its limit with the torso upright, the leg itself has to tip top-forward, with the ankle behind the hip. The forward-pointing foot supports that posture: the toe reaches 0.26 m ahead of the ankle.

## Round 2 plan: get a working balance loop first, with a gentle bounce

| Joint | Controller |
|---|---|
| **Hip (a0)** | Keeps the torso upright: −1.0·obs[1] − 0.05·obs[7]. These gains are about 3–6× lower than before and are stable at this step size. |
| **Ankle (a2)** | Controls the absolute angle of the leg, `θ_leg = −obs[1] + obs[2] + obs[3]`, towards −0.35 (top tipped forward), with damping on its rate. It is a reflex unit with output capped at ±0.15, so it never tips the foot onto its heel or toe. A bias of −0.06 carries the static weight in front of the ankle. Holding the leg tipped forward is what keeps the thigh near −0.15 rad, away from its limit. |
| **Knee (a1)** | Moderate PD to −0.2 rad, which leaves room to extend. A small 2.5 Hz rhythm (0.25 × cos) tests whether the robot bounces without losing balance. |

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