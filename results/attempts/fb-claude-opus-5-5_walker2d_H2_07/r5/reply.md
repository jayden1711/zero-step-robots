# Round 5 (final): stop pushing the thighs into their limit, and add ankle balance

## Why every round so far drifted backward

The thigh joint cannot go past 0. In every episode the thighs peaked at about 0.04 to 0.13 rad, even with saturated positive torque. When a thigh sits at that limit, the limit absorbs any positive hip torque, so nothing reaches the torso.

- **Round 4:** both thighs were pinned at about 0. The balance loop asked for positive torque to pitch the torso forward, but that torque had no effect. The body became one rigid stick with its feet ahead of the hips, and it fell backward.
- **Rounds 0 to 3:** the swing thigh was pinned in the same way. Only the negative stance torque acted on the torso, and it pitched the torso backward. The net effect was a steady backward drift.

Two more facts follow from the geometry:

- **Hip balance needs slack.** It only works while the stance thigh is behind the torso axis (q < 0).
- **Foot placement depends on torso lean.** The swing foot can land ahead of the hip only if the torso leans back a little.
- **The ankle is the other lever.** Each foot extends forward from its ankle, so it can hold the body only while the body is ahead of the ankle.

## Round 5 design

**Rhythm:** 1.2 Hz, legs in antiphase (coupling weight 3). Stance is when sin φ > 0.

**Thighs**
- **Swing (gated by phase):** about +0.7 torque. This brings the leg forward to the limit. Pinning the swing leg is harmless, because it then puts no torque on the torso.
- **Stance:** about −0.1, a slight push backward.
- **Balance on both thighs:** −2·(obs[1] + 0.1·obs[8] + 0.12·obs[10]).
  - In stance this holds the torso at about −0.05 − 0.1·v rad. It leans back more at higher speed, so the swing foot lands further ahead.

**Knees:** torque = 0.1 + 0.8·cos(φ − 0.76) − 0.1·knee velocity.
- The knee is held straight through stance and at touchdown.
- It flexes from liftoff to mid-swing (φ ≈ 3.9) to clear the foot.

**Feet**
- **Ankle balance:** foot torque = 0.2 − 0.36·obs[8] − 1.2·foot angle − 0.05·foot velocity.
- **Starting off:** a positive foot torque tips the body forward, which starts the gait forward.
- **Holding speed:** as speed rises, the term turns into plantarflexion, which brakes the body. This regulates speed near 0.5 m/s.
- **Ankle stiffness:** the foot-angle term acts like an ankle spring and holds the forward lean.
- **Swing:** the bias lifts the toes for clearance.

This is untested. It is my best reading of the data, not a verified result.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.3, "a3": 0.3, "a1": 0.1, "a4": 0.1, "a2": 0.2, "a5": 0.2},
 "units": [
   {"type": "reflex", "name": "R_swing_stance_gate", "inputs": {"sin(R)": -1.0}, "threshold": 0.0,
    "sharpness": 3.0, "to": {"a0": 0.4}},
   {"type": "reflex", "name": "L_swing_stance_gate", "inputs": {"sin(L)": -1.0}, "threshold": 0.0,
    "sharpness": 3.0, "to": {"a3": 0.4}},
   {"type": "linear", "name": "torso_balance_speed", "inputs": {"obs[1]": 1.0, "obs[8]": 0.1, "obs[10]": 0.12},
    "range": 1.5, "tol": 0.05, "to": {"a0": -2.0, "a3": -2.0}},
   {"type": "linear", "name": "R_knee", "inputs": {"cos(R)": 0.58, "sin(R)": 0.551, "obs[12]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee", "inputs": {"cos(L)": 0.58, "sin(L)": 0.551, "obs[15]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_ankle_balance", "inputs": {"obs[4]": 1.0, "obs[13]": 0.04, "obs[8]": 0.3},
    "range": 2.0, "tol": 0.05, "to": {"a2": -1.2}},
   {"type": "linear", "name": "L_ankle_balance", "inputs": {"obs[7]": 1.0, "obs[16]": 0.04, "obs[8]": 0.3},
    "range": 2.0, "tol": 0.05, "to": {"a5": -1.2}}
 ]}
```