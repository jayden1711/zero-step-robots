## Round 3: lean forward, a stronger scissor, and ankle push-off

**Why rounds 1 and 2 drifted backward.** In round 2 the torso controller worked: it held θ near the −0.2 target from 0.1 to 0.4 s. Yet x fell steadily even while both feet were down, and it then sped up into a backward fall. The likely cause is the foot geometry. Walker2d's foot extends forward from the ankle, so the heel is at the ankle and the base of support runs from the ankle to about 0.2 m ahead of it. At the start the centre of mass sits right over the heel. Commanding a backward lean pushed it behind the support, and nothing could stop the backward fall. The robot was also not really stepping: the thighs moved only 0.24 rad because the scissor was too weak for legs of about 9.5 kg.

**Changes**

- **Torso target is now slightly forward, with speed regulation.**
  - θref = 0.05 − 0.15·v, where v = obs[8].
  - At rest the torso leans slightly forward, which shifts weight over the feet and starts forward motion.
  - If the robot speeds up, the target leans back. That lets the swing foot land further ahead (α ≤ −θ), which brakes the fall.
  - If it moves backward, the target leans forward.
  - Same common-mode PD as round 2 (Kt = 3, Ktd = 0.16). It adds −0.45·obs[8], with a bias of +0.075 per hip.
- **Scissor about twice as stiff, with more amplitude.** δref = 0.6·cos φ_R, K = 3, D = 0.3.
  - For one swinging leg (I ≈ 3.7, gravity stiffness about 0.47 per rad), this gives ω_n ≈ 9.7 rad/s and ζ ≈ 0.4.
  - The gait drives it at 5.65 rad/s (0.9 Hz), so the tracking lag stays modest.
  - It still puts zero net torque on the torso.
- **Ankle push-off reflex.** In late stance (sin φ − cos φ > 0.8, roughly φ ∈ [1.4, 3.3]) the foot gets −0.25, which presses the toe down for propulsion. Elsewhere it gets 0, because the bias cancels the reflex's off-state.
- **Unchanged.** The knee PD and the swing-flexion reflex stay the same. The frequency rises to 0.9 Hz for quicker catching steps.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.075, "a1": -0.4, "a2": -0.125, "a3": 0.075, "a4": -0.4, "a5": -0.125},
 "units": [
   {"type": "linear", "name": "torso_balance_common_speed",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.16, "obs[8]": -0.45},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": 0.5}},
   {"type": "linear", "name": "hip_scissor_diff",
    "inputs": {"cos(R)": 0.9, "cos(L)": -0.9, "obs[2]": -3.0, "obs[5]": 3.0, "obs[11]": -0.3, "obs[14]": 0.3},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"sin(R)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a1": -0.6}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"sin(L)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a4": -0.6}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "R_foot_pushoff",
    "inputs": {"sin(R)": 1.0, "cos(R)": -1.0}, "threshold": 0.8, "sharpness": 4.0,
    "to": {"a2": -0.125}},
   {"type": "reflex", "name": "L_foot_pushoff",
    "inputs": {"sin(L)": 1.0, "cos(L)": -1.0}, "threshold": 0.8, "sharpness": 4.0,
    "to": {"a5": -0.125}}
 ]}
```