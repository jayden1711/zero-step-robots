I can't run this, so the design is reasoned from the physics. A few choices are deliberate:

**Rhythm.** Two oscillators, `R` and `L`, run at 0.9 Hz. They are coupled both ways with a lag of π, so they settle into antiphase. They start at π/2 and 3π/2: the right leg in mid-stance and the left in mid-swing. At that point every rhythmic target matches the initial standing posture, so there is no jerk at step 0.

**Hips are split into two modes.** I don't gate by stance or swing, because the network can't multiply cleanly.
- **Scissor mode** (a0 = +S, a3 = −S) tracks the angle between the legs, q_R − q_L, towards 0.5·(cos φR − cos φL)/2·2. That is a ±0.5 rad inter-leg swing.
  - It uses PD gains of 3 and 0.5.
  - Equal and opposite hip torques cancel at the torso, so this mode moves the legs without tipping the torso.
- **Common mode** (C added to both hips) is the torso balance: C = −1.0·obs[1] − 0.08·obs[10] − 0.1·obs[8] − 0.08.
  - Only this mode reacts on the torso.
  - The sign is chosen so the correction opposes torso angle and torso angular velocity.
  - It also regulates speed: the torso leans further back as forward speed rises, with a set-point of about −0.08 rad at rest.
  - The slight backward lean exists because the hips can only extend behind the torso line (thigh range ≤ 0), so the torso must lean back a little for the front foot to land ahead of the hip.

**Knees** are PD-controlled with gains of 3 and 0.25.
- The target comes from a sharp reflex on −sin φ.
- In stance the target is about −0.03 rad, nearly straight, so the leg can carry the weight.
- In swing it flexes to about −0.63 rad, which lifts the foot clear of the ground.

**Ankles** use a soft PD (gains 0.4 and 0.02).
- A small phase-locked target tilts the toe up before touchdown and down at the end of stance, giving a mild push-off.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.08, "a3": -0.08, "a1": -0.99, "a4": -0.99},
 "units": [
   {"type": "linear", "name": "hip_scissor",
    "inputs": {"cos(R)": 0.75, "cos(L)": -0.75, "obs[2]": -3.0, "obs[5]": 3.0, "obs[11]": -0.5, "obs[14]": 0.5},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "torso_balance_speed",
    "inputs": {"obs[1]": -1.0, "obs[10]": -0.08, "obs[8]": -0.1},
    "range": 1.5, "tol": 0.03, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "knee_R_pd",
    "inputs": {"obs[3]": -3.0, "obs[12]": -0.25},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L_pd",
    "inputs": {"obs[6]": -3.0, "obs[15]": -0.25},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_R_swing_flex",
    "inputs": {"sin(R)": -1.0}, "threshold": 0.2, "sharpness": 3.0, "to": {"a1": -0.9}},
   {"type": "reflex", "name": "knee_L_swing_flex",
    "inputs": {"sin(L)": -1.0}, "threshold": 0.2, "sharpness": 3.0, "to": {"a4": -0.9}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"cos(R)": 0.076, "sin(R)": -0.025, "obs[4]": -0.4, "obs[13]": -0.02},
    "range": 0.8, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"cos(L)": 0.076, "sin(L)": -0.025, "obs[7]": -0.4, "obs[16]": -0.02},
    "range": 0.8, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```