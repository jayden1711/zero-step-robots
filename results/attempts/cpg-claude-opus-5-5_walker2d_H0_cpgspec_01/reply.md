This is a CPG-timed walking controller in the style of SIMBICON. I couldn't simulate it, so whether it actually walks is untested.

**How it works**
- **Oscillator:** One oscillator sets the step timing. Its rate rises a little with forward speed (`obs[8]`).
- **Torso and hips:** The torso weighs only about 3.7 kg of the robot's roughly 24 kg, so I split hip control into two parts:
  - **Leg swing:** Equal and opposite hip torques drive the angle between the two hips toward a sine wave. The swing leg goes forward and the stance leg pushes back, with no net torque on the torso.
  - **Torso balance:** A shared torque on both hips holds the torso tilted back by 0.3 rad. In my reading of the model, the hip joint can only move backward from the torso line (range −150° to 0). Tilting the torso back is what lets the swing leg reach in front of the body.
- **Speed feedback on step length:** Four units multiply forward speed by sin(phase). Steps get longer when the robot moves faster and shorter when it is slow, which helps it recover.
- **Knees:** Each knee is held straight (pushed against its 0 limit) during stance. A timed unit bends the knee during mid-swing and also lifts the toes for ground clearance.
- **Ankles:** A soft controller keeps each foot level with the ground. A small extra ankle torque slows the robot above about 0.6 m/s and gives a gentle push below it.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "gait", "freq_hz": 0.65, "phase0": 0.0, "feedback": {"obs[8]": 1.5}}],
 "couplings": [],
 "bias": {"a1": -0.45, "a4": -0.45, "a2": 0.08, "a5": 0.08},
 "units": [
  {"type": "reflex", "name": "hipR", "inputs": {"obs[1]": 1.5, "obs[2]": -4.3, "obs[5]": 4.3, "obs[10]": 0.055, "obs[11]": -0.43, "obs[14]": 0.43, "sin(gait)": 1.075, "cos(gait)": 0.72}, "threshold": 0.45, "sharpness": 1.0, "to": {"a0": 1.0}},
  {"type": "reflex", "name": "hipL", "inputs": {"obs[1]": 1.5, "obs[2]": 4.3, "obs[5]": -4.3, "obs[10]": 0.055, "obs[11]": 0.43, "obs[14]": -0.43, "sin(gait)": -1.075, "cos(gait)": -0.72}, "threshold": 0.45, "sharpness": 1.0, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "kneeR", "inputs": {"obs[3]": -2.0, "obs[12]": -0.14}, "threshold": -0.1, "sharpness": 1.0, "to": {"a1": 1.0}},
  {"type": "reflex", "name": "kneeL", "inputs": {"obs[6]": -2.0, "obs[15]": -0.14}, "threshold": -0.1, "sharpness": 1.0, "to": {"a4": 1.0}},
  {"type": "reflex", "name": "ankleR", "inputs": {"obs[1]": -1.0, "obs[2]": -1.0, "obs[3]": -1.0, "obs[4]": -1.0, "obs[13]": -0.06, "obs[8]": -0.4}, "threshold": -0.24, "sharpness": 1.0, "to": {"a2": 0.5}},
  {"type": "reflex", "name": "ankleL", "inputs": {"obs[1]": -1.0, "obs[5]": -1.0, "obs[6]": -1.0, "obs[7]": -1.0, "obs[16]": -0.06, "obs[8]": -0.4}, "threshold": -0.24, "sharpness": 1.0, "to": {"a5": 0.5}},
  {"type": "reflex", "name": "swingflexR", "inputs": {"cos(gait)": 0.9394, "sin(gait)": -0.3429}, "threshold": 0.4, "sharpness": 6.0, "to": {"a1": -0.45, "a2": 0.08}},
  {"type": "reflex", "name": "swingflexL", "inputs": {"cos(gait)": -0.9394, "sin(gait)": 0.3429}, "threshold": 0.4, "sharpness": 6.0, "to": {"a4": -0.45, "a5": 0.08}},
  {"type": "reflex", "name": "prod1", "inputs": {"obs[8]": 0.35, "sin(gait)": 0.5}, "threshold": -0.6585, "sharpness": 1.0, "to": {"a0": -2.0, "a3": 2.0}},
  {"type": "reflex", "name": "prod2", "inputs": {"obs[8]": -0.35, "sin(gait)": -0.5}, "threshold": -0.6585, "sharpness": 1.0, "to": {"a0": -2.0, "a3": 2.0}},
  {"type": "reflex", "name": "prod3", "inputs": {"obs[8]": 0.35, "sin(gait)": -0.5}, "threshold": -0.6585, "sharpness": 1.0, "to": {"a0": 2.0, "a3": -2.0}},
  {"type": "reflex", "name": "prod4", "inputs": {"obs[8]": -0.35, "sin(gait)": 0.5}, "threshold": -0.6585, "sharpness": 1.0, "to": {"a0": 2.0, "a3": -2.0}}
 ]}
```