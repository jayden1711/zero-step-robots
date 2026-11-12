## Round 1 design

### What went wrong in round 0

All 10 runs fell the same way. The torso pitched backward within 0.1 s, to −0.55 rad, and the robot then drifted backward until the torso angle passed −1.

The cause is the thigh control. Both thighs had a constant bias of −0.75, and they were held stiffly toward a *joint* angle of −0.3. With the feet on the ground, driving the joint angle negative rotates the torso backward instead of moving the leg. That joint stiffness (gain 2) was larger than the torso feedback (gain 1), so it won. The thighs were also saturated about 70% of the time.

### Changes in round 1

- **Thigh PD now targets the leg's angle in the world frame, not the joint angle.**
  - The leg's forward angle in the world is φ_w = q_thigh − obs[1].
  - The PD term is Kp·(φ* − q + obs[1]) − Kd·(q̇ − obs[10]).
  - With the foot planted, this term no longer moves the torso, so torso control and leg tracking stay separate.
- **Torso PD now dominates the thigh command.**
  - The term is −3·(obs[1] − lean) − 0.12·obs[10] at each thigh.
  - The damping is chosen to stay well inside the stability limit for the 0.008 s step.
- **The lean target is −0.2 rad (slightly back).**
  - Thigh angles must stay ≤ 0, so a backward lean is the only way the swing foot can land ahead of the hip.
  - The constant thigh bias is now only the lean term (−0.6). It is cancelled once the torso reaches its target.
- **The rhythm amplitude is ±0.25 rad around a vertical leg.** The two legs are in antiphase, so their torques largely cancel on the torso.
- **Knees, feet and oscillators are unchanged.**

### The thigh unit, term by term

| Input | Coefficient | Source |
|---|---|---|
| obs[1] (torso angle) | −1.5 | Kp − Kt = 1.5 − 3 |
| thigh angle | −1.5 | −Kp |
| torso angular velocity | +0.08 | Kd − Kdt = 0.2 − 0.12 |
| thigh velocity | −0.2 | −Kd |
| sin(phase) | 0.375 | Kp · 0.25 |
| bias | −0.6 | Kt · lean = 3 · (−0.2) |

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.5708}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.1416},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.1416}
 ],
 "bias": {"a0": -0.6, "a3": -0.6, "a1": -0.7, "a4": -0.7},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[1]": -1.5, "obs[2]": -1.5, "obs[10]": 0.08, "obs[11]": -0.2, "sin(R)": 0.375},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[1]": -1.5, "obs[5]": -1.5, "obs[10]": 0.08, "obs[14]": -0.2, "sin(L)": 0.375},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -2.0, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -2.0, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.6}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.6}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```