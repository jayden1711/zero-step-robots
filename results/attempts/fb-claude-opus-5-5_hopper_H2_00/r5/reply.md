# Round 5 (final): keep round 4's stable base and push for forward motion

## What round 4 showed

- **The balance signs are right.** All 10 episodes survived the full 8 s, and none of the units saturated.
- **The robot did not hop or move.** The foot was on the ground 99% of the time, and the torso rocked at the 2.5 Hz rhythm between about 0 and −0.08 rad, so mean speed was zero.
- **The lean target was never reached.** The intended torso lean was +0.04 rad (forward), but the actual mean was about −0.035 (slightly back). The ankle loop's set-point was holding the body back against the hip.

A standing controller scores about 0 m and fails. Even a forward fall scores better than that. So in this final round I keep round 4's structure and signs, and push for forward hopping.

## Round 5 changes

| | Round 4 | Round 5 |
|---|---|---|
| Hip bias (lean target) | 0.10 | 0.20 |
| Hip speed feedback (obs[5]) | −0.08 | −0.15 |
| Ankle set-point (threshold) | −0.02 | −0.08 |
| Knee crouch/extend rhythm | 0.35 | 0.70 |
| Foot toe-down push | 0.12 | 0.25 |
| Thigh swing rhythm | 0.15 | 0.25 |
| Frequency | 2.5 Hz | 2.5 Hz |

What each change is for:

- **Forward lean:** the larger hip bias aims for about +0.08 rad of lean.
- **Speed limit:** the stronger obs[5] term reduces the lean as speed rises, at about 0.04 rad per m/s.
- **Ankle set-point:** the lower threshold lets the ankle allow a forward body lean instead of resisting it.
- **Real hopping:** the knee rhythm is doubled to 0.7, so the knee crouches and extends hard enough to lift off. The toe-down foot push is timed with the knee extension.
- **Leg swing in flight:** the thigh rhythm increases to 0.25 to swing the leg forward while the foot is in the air.
- **Torque budget:** a peak knee command of 0.7 + 0.1 bias + PD stays within ±1.

I can't test this before it is scored, so it is a deliberate gamble. If the hop rhythm destabilises the torso, this design may fall early. I chose it because a stable but stationary controller cannot pass.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 0.1},
 "units": [
   {"type": "linear", "name": "hip_torso", "inputs": {"obs[1]": -2.5, "obs[7]": -0.3, "obs[5]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": -0.25},
    "range": 0.3, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd", "inputs": {"obs[3]": -1.5, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_rhythm", "inputs": {"sin(cpg)": 0.7},
    "range": 0.8, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "ankle_balance",
    "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.2, "obs[8]": 0.2, "obs[9]": 0.2},
    "threshold": -0.08, "sharpness": 8.0, "to": {"a2": 0.15}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_push", "inputs": {"sin(cpg)": -0.25},
    "range": 0.3, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```