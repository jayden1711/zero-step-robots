# Round 5 (final): lean the body forward over the feet before stepping

**What all four failures share.** Every design ended up with the robot as a rigid stick tipping backward. In rounds 2 to 4:

- The torso settled near −0.25 whatever its target was.
- The thighs pinned near q = 0, so leg lean β = q − θ ≈ +0.25. The feet were ahead of the hip the whole time.
- The stance legs never got behind the hip, so the centre of mass never got ahead of the ankles. Nothing ever pushed the body forward.

Hip torques cannot fix this. They mainly spin the light torso, and leaning the torso back moves the centre of mass further back.

**The new lever is the ankle.** The heel is at the ankle and the sole runs about 0.26 m forward of it. So the ankle can make the whole body lean forward over the long foot:

- Toe-up torque rocks the body onto the heel, which tips it forward.
- The forward sole then carries the centre of pressure, so the lean is caught.
- The legs tilting forward also unpins the hips (q = β + θ < 0). That gives the swing leg room to come forward.

**Changes**

- **Ankle PD with a forward-lean reference.**
  - Torque = 0.8·(0.15 − q_foot) − 0.03·q̇_foot − 0.15·v.
  - With ankle stiffness below the gravity stiffness, the body falls slowly *forward*. The steps then catch it, so any failure should now cost forward distance, not backward.
  - The speed term brakes with toe-down torque when the robot goes fast and pushes forward when it drifts back.
  - In swing the toe lifts, which helps clearance.
- **Torso target near upright, leaning back with speed.** θref = −0.05 − 0.25·v. At speed, the extra back lean lets the swing foot land further ahead of the hip, which brakes.
- **Scissor.** A = 0.5 and K = 2.5, with zero net torque on the torso.
- **Cadence follows speed.** Oscillator rate gets +1.5 rad/s per m/s of obs[8].
- **Unchanged.** The knee scheme is the same as round 4. The start is at R = π/2 and L = 3π/2, so the scissor reference matches the closed-leg start.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708, "feedback": {"obs[8]": 1.5}},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.71239, "feedback": {"obs[8]": 1.5}}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.075, "a1": -0.45, "a2": 0.12, "a3": -0.075, "a4": -0.45, "a5": 0.12},
 "units": [
   {"type": "linear", "name": "torso_balance_common_speed",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.16, "obs[8]": -0.75},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": 0.5}},
   {"type": "linear", "name": "hip_scissor_diff",
    "inputs": {"cos(R)": 0.625, "cos(L)": -0.625, "obs[2]": -2.5, "obs[5]": 2.5, "obs[11]": -0.25, "obs[14]": 0.25},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"sin(R)": -1.0}, "threshold": 0.2, "sharpness": 6.0,
    "to": {"a1": -0.65}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"sin(L)": -1.0}, "threshold": 0.2, "sharpness": 6.0,
    "to": {"a4": -0.65}},
   {"type": "linear", "name": "R_ankle_lean_pd",
    "inputs": {"obs[4]": -0.8, "obs[13]": -0.03, "obs[8]": -0.15},
    "range": 1.2, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_ankle_lean_pd",
    "inputs": {"obs[7]": -0.8, "obs[16]": -0.03, "obs[8]": -0.15},
    "range": 1.2, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```