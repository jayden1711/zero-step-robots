## Round 3 design

### What went wrong in round 2

The thighs barely moved: they stayed between −0.12 and +0.03, pressed against the 0 limit. The torso settled about 0.2 rad back.

- **Feet always ahead of the hip.** Because the thigh can only go behind the torso line, a back lean with straight thighs points both legs about 0.2 rad forward. Planted feet ahead of the hip push the body backward, so it drifted back at −0.7 m/s.
- **Leg control and torso control fought.** Both were ungated and applied to both hips, so the torso term (−2θ ≈ +0.4) pinned the swing leg at the limit. The stance-leg PD also kept twisting the torso.

### Changes in round 3: a SIMBICON-style split

**Swing-leg placement is now gated by phase.**
- Each leg has a pair of reflex units. Each unit sees the world-frame leg error e = φ\* − (q − θ), minus a world-frame damping term.
- The two units carry opposite phase offsets ±2(cos φ − 0.5).
- The pair sums to a PD response with no offset during swing (cos φ > 0). In stance both units saturate in opposite directions and cancel, so the stance leg gets nothing.
- The peak stiffness is about 4, and each unit is bounded at ±0.8.

**Foot placement is regulated by speed.**
- The placement target is φ\* = 0.2·v.
- At rest the swing foot lands slightly behind the hip, so the body tips forward and speeds up. At higher speed the foot lands further ahead, which brakes.

**The reaction torque is compensated.**
- The same swing units also send −0.5 × the swing torque to the other hip, which is in stance.
- This cancels most of the reaction that swinging the leg puts on the torso.

**The torso PD is one shared linear unit sent to both hips.**
- It is −2·θ − 0.1·θ̇, with bias −0.2, giving a lean target of −0.1.
- The swing pair no longer has the large competing torso gain.

**The knees flex more for ground clearance.**
- The swing target is about −0.58.
- The stance knee is still held straight.

**Feet and oscillators are unchanged.** This uses 11 of the 16 units.

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
 "bias": {"a0": -0.2, "a3": -0.2, "a1": -0.85, "a4": -0.85},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[10]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "reflex", "name": "swing_R_p", "inputs": {"obs[2]": -1.0, "obs[1]": 1.0, "obs[8]": 0.2, "obs[11]": -0.1, "obs[10]": 0.1, "cos(R)": 0.8},
    "threshold": 0.4, "sharpness": 2.5, "to": {"a0": 0.8, "a3": -0.5}},
   {"type": "reflex", "name": "swing_R_m", "inputs": {"obs[2]": -1.0, "obs[1]": 1.0, "obs[8]": 0.2, "obs[11]": -0.1, "obs[10]": 0.1, "cos(R)": -0.8},
    "threshold": -0.4, "sharpness": 2.5, "to": {"a0": 0.8, "a3": -0.5}},
   {"type": "reflex", "name": "swing_L_p", "inputs": {"obs[5]": -1.0, "obs[1]": 1.0, "obs[8]": 0.2, "obs[14]": -0.1, "obs[10]": 0.1, "cos(L)": 0.8},
    "threshold": 0.4, "sharpness": 2.5, "to": {"a3": 0.8, "a0": -0.5}},
   {"type": "reflex", "name": "swing_L_m", "inputs": {"obs[5]": -1.0, "obs[1]": 1.0, "obs[8]": 0.2, "obs[14]": -0.1, "obs[10]": 0.1, "cos(L)": -0.8},
    "threshold": -0.4, "sharpness": 2.5, "to": {"a3": 0.8, "a0": -0.5}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -3.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -3.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.9}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.9}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```