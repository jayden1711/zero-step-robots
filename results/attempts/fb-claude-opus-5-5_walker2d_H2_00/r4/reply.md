## Round 4: start mid-stride, lean the torso back, and keep the knees straight at t = 0

**What rounds 2 and 3 actually showed.** The torso controller never failed on its own terms. In round 3, the target was θ = +0.05, but the torso sat at −0.25 while both thighs stayed pinned near q = 0, their upper joint limit. With q = 0, torso and legs form one rigid stick. Positive hip torque then just presses against the limit and cannot bring the torso forward. The stick leaned back on its heels and fell.

**What starts the backward rotation.** At t = 0, the left leg started in mid-swing, so its knee reflex flexed it hard (about −1.0) while the foot was still loaded. The reaction of that knee torque pushes the left thigh towards positive q, which is blocked by the limit. That torque passes straight into the torso and pitches it backward: θ was already −0.14 at 0.1 s. Round 3's ankle push-off made things slightly worse, because toe-down torque pitches the leg backward.

**Geometry this design relies on.**
- The heel is at the ankle, so the ankle can only brake a forward fall. It cannot stop a backward one.
- The hip only lets a leg sit at or behind the torso axis (q ≤ 0), so leg lean = θ − q ≥ θ.

So the posture should be:
- The torso leans back somewhat. This gives the hips margin from the limit and lets the front foot land ahead of the hip.
- The legs straddle the vertical.
- The body is always moving forward over the stance foot.

**Changes**
- **Starting phases.** R = 1.87 (just past mid-stance, so the body is already over and slightly ahead of the R foot) and L = 5.01 (late swing).
  - The scissor's initial command drives the stance leg backward. That pushes the body forward.
- **Torso target.** θref = −0.15 − 0.1·v.
  - The back lean keeps q off its limit and lets the front foot land ahead of the hip.
  - Faster speed puts the catching foot further forward.
  - Same Kt = 3 and Ktd = 0.16 as before.
- **Scissor.** A = 0.5 and K = 2 (lower than round 3). This avoids saturating the thigh actions, which in round 3 wiped out the common-mode torso torque half the time.
- **Knee.** Bias −0.45 and reflex ±0.65, with threshold 0.2 and sharpness 6.
  - Stance: +0.2, locking the knee straight.
  - Swing: −1.1, settling near −0.73 rad.
  - Near touchdown (sin ≈ 0) the knee is already straight.
- **Feet.** The push-off reflex is removed. The ankle PD is softer (Kp 0.5), so the body can roll over the foot.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.87},
   {"name": "L", "freq_hz": 0.9, "phase0": 5.01}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.225, "a1": -0.45, "a2": 0.0, "a3": -0.225, "a4": -0.45, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_common_speed",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.16, "obs[8]": -0.3},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": 0.5}},
   {"type": "linear", "name": "hip_scissor_diff",
    "inputs": {"cos(R)": 0.5, "cos(L)": -0.5, "obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.25, "obs[14]": 0.25},
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
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```