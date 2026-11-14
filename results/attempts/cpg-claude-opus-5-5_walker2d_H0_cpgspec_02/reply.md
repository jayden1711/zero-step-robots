This is a timed walking controller built from one oscillator and PD control, in the style of the SIMBICON biped controller. I designed it from my reading of the Walker2d model and could not test it, so whether it walks is unverified.

**Assumptions about the model.** These come from memory of the MuJoCo file. If the torso-angle sign is reversed, the torso controller will push the wrong way.
- All hinges, including the torso pitch, rotate about the same axis. A positive joint angle moves the lower end of a limb forward, and a positive torso angle means leaning back.
- The hip and knee can only bend in the negative direction (0 to −150°). So the thighs can only reach forward of vertical if the torso leans back.
- The legs are about 85% of the 24 kg mass and the torso is light. Leaning back costs little balance, but hip torques easily jerk the torso around.

**How the controller works.**
- **Posture:** the torso leans back about 0.25 rad, so the hip limits still allow a forward step of about ±0.22 rad.
- **Oscillator:** one oscillator at 0.9 Hz. The right leg swings while sin(p) > 0 and the left leg swings in the other half of the cycle.
- **Hips:**
  - Each hip uses PD control in joint space. The swing damping uses the thigh's absolute angular velocity so it doesn't make the light torso unstable.
  - One feedforward unit drives both hips in opposite directions. It includes the target-velocity term, so the two feedforward torques cancel on the torso.
  - A velocity term (0.18 rad per m/s around a target of 0.7 m/s) steps further forward and brakes when walking too fast, and does the opposite when too slow.
- **Torso balance:** four units add extra torso stiffness and damping, mostly to the stance hip. Each pair, tanh(x+G) + tanh(x−G), acts as a gate driven by the phase.
- **Knees:** each knee is held straight against its limit during stance. A smooth reflex driven by the phase bends it about 0.85 rad during swing for ground clearance.
- **Ankles:** each ankle is held flat by PD control and lifts the toe about 0.2 rad during swing.
- **Gains:** the gains are kept within what the 0.008 s control step can handle without becoming unstable.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "osc", "freq_hz": 0.9, "phase0": 1.37}],
 "couplings": [],
 "bias": {"a0": -1.065, "a3": -1.065, "a1": -1.2, "a4": -1.2, "a2": 0.15, "a5": 0.15},
 "units": [
  {"type": "linear", "name": "hipR_fb", "inputs": {"obs[2]": -2.5, "obs[11]": -0.35, "obs[10]": -0.32, "obs[8]": 0.45},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0}},
  {"type": "linear", "name": "hipL_fb", "inputs": {"obs[5]": -2.5, "obs[14]": -0.35, "obs[10]": -0.32, "obs[8]": 0.45},
   "range": 4.0, "tol": 0.02, "to": {"a3": 1.0}},
  {"type": "linear", "name": "hip_ff", "inputs": {"cos(osc)": -0.646, "sin(osc)": 0.764},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.701, "a3": -0.701}},
  {"type": "reflex", "name": "torso_R_plus", "inputs": {"obs[1]": 3.0, "obs[10]": 0.07, "sin(osc)": 1.5},
   "threshold": -0.3, "sharpness": 1.0, "to": {"a0": 0.8}},
  {"type": "reflex", "name": "torso_R_minus", "inputs": {"obs[1]": 3.0, "obs[10]": 0.07, "sin(osc)": -1.5},
   "threshold": 1.8, "sharpness": 1.0, "to": {"a0": 0.8}},
  {"type": "reflex", "name": "torso_L_plus", "inputs": {"obs[1]": 3.0, "obs[10]": 0.07, "sin(osc)": -1.5},
   "threshold": -0.3, "sharpness": 1.0, "to": {"a3": 0.8}},
  {"type": "reflex", "name": "torso_L_minus", "inputs": {"obs[1]": 3.0, "obs[10]": 0.07, "sin(osc)": 1.5},
   "threshold": 1.8, "sharpness": 1.0, "to": {"a3": 0.8}},
  {"type": "linear", "name": "kneeR_fb", "inputs": {"obs[3]": -3.0, "obs[12]": -0.25},
   "range": 4.0, "tol": 0.02, "to": {"a1": 1.0}},
  {"type": "linear", "name": "kneeL_fb", "inputs": {"obs[6]": -3.0, "obs[15]": -0.25},
   "range": 4.0, "tol": 0.02, "to": {"a4": 1.0}},
  {"type": "reflex", "name": "swingR_knee_toe", "inputs": {"sin(osc)": 0.955, "cos(osc)": 0.296},
   "threshold": 0.2, "sharpness": 4.0, "to": {"a1": -1.35, "a2": 0.15}},
  {"type": "reflex", "name": "swingL_knee_toe", "inputs": {"sin(osc)": -0.955, "cos(osc)": -0.296},
   "threshold": 0.2, "sharpness": 4.0, "to": {"a4": -1.35, "a5": 0.15}},
  {"type": "linear", "name": "ankleR_fb", "inputs": {"obs[4]": -1.5, "obs[13]": -0.03},
   "range": 3.0, "tol": 0.02, "to": {"a2": 1.0}},
  {"type": "linear", "name": "ankleL_fb", "inputs": {"obs[7]": -1.5, "obs[16]": -0.03},
   "range": 3.0, "tol": 0.02, "to": {"a5": 1.0}}
 ]}
```