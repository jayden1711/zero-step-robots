This is a phase-driven PD controller with world-referenced torso balance. I couldn't run any of it, so the gains come from hand estimates, not tests.

**Leg geometry.** I'm working from the stock Walker2d model as I remember it. The thigh joint range is [-150°, 0°], so a thigh can only swing back from in line with the torso. A front foot can only land ahead of the hip if the torso leans back.

**Torso and scissor gait.** Both hips hold the torso at -0.25 rad (leaning back) in world terms. The thigh joint targets run from -0.55 to +0.05, which makes the legs sweep about ±0.27 rad around vertical in a scissor pattern. The torso is light compared with the legs, so the common part of the hip torques balances the torso. The difference between the two hip torques drives the scissor, so the stance hip provides the forward push.

**Joint control.**
- **Knees:** each knee is held straight against its joint limit during stance. A flexion pulse fires in mid-swing (window φ ≈ 3.55 to 5.87 for the right leg) to lift the foot clear.
- **Ankles:** each foot is kept level with the ground in world terms, so it lands flat and the ankle is free in stance. A plantarflexion push-off pulse fires in late stance.

**Oscillator.** One oscillator drives both legs; the left leg uses the negated cos/sin, which puts it exactly half a cycle behind. If the walker speeds up, the stepping rate rises (feedback from forward velocity, obs[8]), so each foot lands sooner and further forward relative to the body, which brakes it. The base rate is 0.55 Hz, rising by about 0.3 Hz per m/s.

**Start.** The phase starts at 2.3 rad: the right leg is in late stance and the left leg is about to land. This makes the walker tip forward into its first step instead of falling backward.

**Main risk.** Everything above depends on the joint sign conventions I recalled. In particular I assumed the torso joint axis is +y and the leg joint axes are -y. If that is wrong, the torso feedback has the wrong sign and the walker falls immediately.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "gait", "freq_hz": 0.55, "phase0": 2.3, "feedback": {"obs[8]": 2.0}}],
 "couplings": [],
 "bias": {"a0": -1.125, "a3": -1.125, "a1": -0.625, "a4": -0.625, "a2": -0.3, "a5": -0.3},
 "units": [
  {"type": "linear", "name": "hip_R", "inputs": {"obs[2]": -1.5, "obs[11]": -0.1, "obs[1]": -3.0, "obs[10]": -0.03, "cos(gait)": 0.45},
   "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
  {"type": "linear", "name": "hip_L", "inputs": {"obs[5]": -1.5, "obs[14]": -0.1, "obs[1]": -3.0, "obs[10]": -0.03, "cos(gait)": -0.45},
   "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
  {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -1.5, "obs[12]": -0.12},
   "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -1.5, "obs[15]": -0.12},
   "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "foot_level_R", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[13]": -0.03},
   "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "foot_level_L", "inputs": {"obs[1]": 0.5, "obs[5]": -0.5, "obs[6]": -0.5, "obs[7]": -0.5, "obs[16]": -0.03},
   "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}},
  {"type": "reflex", "name": "swing_knee_R", "inputs": {"sin(gait)": -1.0}, "threshold": 0.4, "sharpness": 6.0, "to": {"a1": -0.7}},
  {"type": "reflex", "name": "swing_knee_L", "inputs": {"sin(gait)": 1.0}, "threshold": 0.4, "sharpness": 6.0, "to": {"a4": -0.7}},
  {"type": "reflex", "name": "pushoff_R", "inputs": {"cos(gait)": -0.958, "sin(gait)": 0.288}, "threshold": 0.8, "sharpness": 10.0, "to": {"a2": -0.3}},
  {"type": "reflex", "name": "pushoff_L", "inputs": {"cos(gait)": 0.958, "sin(gait)": -0.288}, "threshold": 0.8, "sharpness": 10.0, "to": {"a5": -0.3}}
 ]}
```