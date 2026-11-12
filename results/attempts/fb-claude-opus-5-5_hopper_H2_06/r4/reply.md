# Round 4 design

## What round 3 showed

Round 3 did not walk. It fell forward slowly, and that fall is where the 1.46 m came from.

- **The foot never left the ground.** It was on the ground for 98% of steps, with only 1 touchdown (the initial landing).
- **The displacement came from leaning.** The x position grew while the foot stayed planted, so the body was tipping forward over a fixed foot. Thigh angle −1.05, foot pinned at −0.80, then height fell below 0.7. Both round 2 and round 3 end at about 1.5 m, which is roughly how far the torso travels when the robot falls over its foot.
- **The ankle cannot fix this.** The foot reaches only 0.26 m ahead of the ankle and 0.13 m behind it. The robot weighs about 15 kg, so the ankle can apply only about ±0.1–0.19 of action before the heel or toe lifts. In round 3 the cap of 0.35 tipped the foot onto its toe, which is why the height rose to 1.39 m.
- **The foot must be replaced.** Its position can't be moved while it is loaded. The only way to move it forward is to unload it with a real hop and swing the leg forward while it is in the air.

## Round 4 changes: a real hop with flight-phase leg swing

| Joint | Change |
|---|---|
| **Knee (a1)** | Rhythm raised from 0.25 to 0.6 around a deeper crouch (bias −0.6, so the mean knee angle is about −0.3). This gives room to extend hard and leave the ground. Thrust peaks at phase 0. |
| **Foot (a2)** | A new push-off term, −0.2·cos (toe down), in phase with the knee thrust. The leg-angle balance reflex stays, but its cap goes back down to 0.2 so the heel and toe stay down during stance. It uses a smaller target lean (−0.3) and keeps the speed feedback. |
| **Hip (a0)** | Torso PD unchanged (−1.5, −0.08). A new swing term, +0.35·sin, adds positive hip torque in the half cycle after thrust (flight). That brings the leg forward toward the straight-under-hip limit before landing. In the other half (stance), the term is negative, which sweeps the leg back and propels the body. |
| **Rhythm** | 2.5 Hz (0.4 s cycle: about 0.2 s stance and 0.2 s flight). |

This is a riskier design, but the round-2/3 posture-holding strategy can't pass 3 m: it tops out at about 1.5 m. If it fails, the touchdown count and torso trace will show whether the hops happen and whether the swing term destabilises the torso.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.6, "a2": -0.04},
 "units": [
   {"type": "linear", "name": "hip_torso_pd_swing",
    "inputs": {"obs[1]": -1.5, "obs[7]": -0.08, "sin(hop)": 0.35},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_thrust",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.6},
    "range": 1.6, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pushoff",
    "inputs": {"cos(hop)": -0.2},
    "range": 0.25, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "ankle_leg_angle_speed",
    "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.2, "obs[8]": 0.2, "obs[9]": 0.2, "obs[5]": -0.3},
    "threshold": -0.42, "sharpness": 6.0, "to": {"a2": 0.2}}
 ]}
```