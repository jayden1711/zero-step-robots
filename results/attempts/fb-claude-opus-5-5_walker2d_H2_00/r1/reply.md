Round 0 failed because the controller drove the torso backward. Both thigh torques sat at about −1 (the bias of −0.5 plus the reference offset). With the feet on the ground, that pitched the torso back to −1 rad within 0.27 s. The data agree with the stated sign conventions:

- x moved −0.17 m. That equals 0.2·sin(1), the arc of the torso root rotating about the hip.
- The stance thigh angle followed the torso angle (q ≈ θ ≈ −1).

The damping was also too stiff for the light torso at dt = 0.008, so the thighs were saturated most of the time.

**Changes**

- **Thigh tracks the absolute leg angle.** Each thigh now tracks α = q − θ, the leg angle in the world frame, instead of the joint angle. The damping uses q̇ − θ̇. In stance α is fixed by the ground, so this tracking no longer adds stiffness or damping to the torso's fast mode.
- **Torso balance is a separate PD.** It holds the torso at θref = −0.2 (slight backward lean). Because the thigh can't go in front of the torso axis (q ≤ 0), this lean is what lets the swing foot land ahead of the hip: α ≤ −θ. The gains are Kt = 1.5 and Ktd = 0.07 per leg, sized so the torso mode stays well damped and stable at dt = 0.008.
- **Leg reference.** α_ref = −0.05 + 0.25·cos φ, which runs from +0.2 to −0.3 rad. Combined thigh coefficients:
  - q: −1
  - θ: Kp − Kt = −0.5
  - q̇: −0.3
  - θ̇: Kd − Ktd = +0.23
  - constant (bias): Kp·α0 + Kt·θref = −0.35
- **Starting phases.** R = π/2 (mid-stance) and L = 3π/2 (mid-swing). At these phases the initial references match the straight-leg start, so there is no large torque at t = 0.
- **Other settings.** The knee is unchanged. The foot damping is reduced. The frequency is 0.8 Hz.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.35, "a1": -0.8, "a2": 0.0, "a3": -0.35, "a4": -0.8, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_abs_torso",
    "inputs": {"cos(R)": 0.25, "obs[2]": -1.0, "obs[1]": -0.5, "obs[11]": -0.3, "obs[10]": 0.23},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.8, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_abs_torso",
    "inputs": {"cos(L)": 0.25, "obs[5]": -1.0, "obs[1]": -0.5, "obs[14]": -0.3, "obs[10]": 0.23},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.8, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```