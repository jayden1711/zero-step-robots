This controller is untested, because I can't run the simulation. Every number below comes from reasoning about the Walker2d model, not from tuning, so it may not walk as intended.

It uses one phase oscillator, with the left leg at its phase + π (exact antiphase). Each joint uses a PD law built from the joint's own angle and velocity, with a phase-dependent target.

**Hips: differential plus common mode**
- **Scissor motion (differential):** one unit drives the difference between the two hip angles, q_R − q_L, towards 2·A·cos(ψ), with A = 0.25. It also adds a little velocity feedforward. The unit outputs +1 to the right hip and −1 to the left. Opposite torques cancel on the torso, so the leg rhythm does not tip the torso.
- **Torso balance (common mode):** a second unit adds the same torque to both hips: 0.7·(θ − θref) + 0.06·θ̇.
  - Positive thigh torque pitches the torso forward. Every joint shares the −y axis with the torso joint, so this sign holds whatever the gait.
  - θref is about 0.35 rad, leaning back. The hip joint's range is [−150°, 0°], so a thigh can only swing behind the torso line. The torso must lean back for the front leg to reach ahead of vertical.
  - θref rises slightly with forward speed, so the robot leans back more when fast.

**Knees**
- PD with gain 2.0 towards +0.15 rad. That holds the knee straight against its 0 limit during stance.
- A swing reflex switches the target to about −0.9 rad over most of the swing phase. It releases just before touchdown so the leg straightens in time.

**Ankles**
- A soft PD (gain 0.6) towards a foot aligned with the shank, which gives a heel-first touchdown.
- The knee reflex also lifts the toe during swing for ground clearance.

**Cadence**
- The phase rate is 2π·0.75 + 2.0·(x-velocity) rad/s. A faster body advances the step sooner, so the swing leg arrives in time to catch it.

**Gains**
- Derivative gains are kept small enough relative to each body's inertia to stay stable at the 0.008 s control step.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 0.75, "phase0": 1.5708, "feedback": {"obs[8]": 2.0}}],
 "couplings": [],
 "bias": {"a0": -0.189, "a3": -0.189, "a1": -0.75, "a4": -0.75, "a2": 0.18, "a5": 0.18},
 "units": [
   {"type": "linear", "name": "hip_scissor",
    "inputs": {"cos(P)": 1.0, "sin(P)": -0.3, "obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.2, "obs[14]": 0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": 0.7, "obs[10]": 0.06, "obs[8]": -0.07},
    "range": 2.0, "tol": 0.02, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "knee_pd_R",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.2},
    "range": 4.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_pd_L",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.2},
    "range": 4.0, "tol": 0.02, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "swing_flex_R",
    "inputs": {"sin(P)": -0.955, "cos(P)": 0.296},
    "threshold": 0.267, "sharpness": 6.0, "to": {"a1": -1.05, "a2": 0.18}},
   {"type": "reflex", "name": "swing_flex_L",
    "inputs": {"sin(P)": 0.955, "cos(P)": -0.296},
    "threshold": 0.267, "sharpness": 6.0, "to": {"a4": -1.05, "a5": 0.18}},
   {"type": "linear", "name": "ankle_pd_R",
    "inputs": {"obs[4]": -0.6, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_pd_L",
    "inputs": {"obs[7]": -0.6, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.02, "to": {"a5": 1.0}}
 ]}
```