This is a SIMBICON-style walker: a 1.2 Hz clock schedules swing and stance, and feedback provides the stability. I couldn't test it, so the gains are physics estimates, not tuned values. It also depends on two recalled details of the model file, listed at the end. If either is wrong, the robot will likely fall early.

**Phase.** One oscillator `P` drives both legs. The right leg swings when φ is in (0, π), and the left leg is half a cycle behind. The gait speeds up slightly as forward speed rises.

**Torso.** One unit adds a PD (proportional-derivative) term on torso angle to both hip torques, holding the torso about 0.25 rad leaned back. The hips can only swing the leg backward of the torso axis, so this lean is what lets the swing foot land ahead of the hip. The torso weighs only about 3.7 kg of 24 kg, so the lean barely moves the centre of mass.

**Swing hips.** Each leg gets a PD controller on the leg's angle in the world frame. Its target uses a velocity correction: the faster the robot moves, the further ahead the foot is placed. The target is about 0.13 rad ahead at the design speed of 0.6 m/s.
- This torque is switched on only during that leg's swing. Each switch uses two reflex units, `½[tanh(b+x) − tanh(b−x)]`, where `b = 1.2(cos(φ−φc) − 1)`. This gives roughly `x · sech²(b)`, a smooth swing-phase window.
- The same torque is subtracted from the stance hip, which cancels its reaction on the light torso.

**Knees.** The knee target is −0.8·sin(φ + 0.3), which bends the knee during swing for ground clearance. During stance the target is positive, so the knee is held straight against its joint stop.

**Ankles.** A PD controller keeps the foot about level, toe slightly up, assuming the torso is at its 0.25 rad lean. In stance this gives almost no torque (a passive ankle). In swing it keeps the toe from catching the ground.

**Assumptions about the model file:**
- Every hinge, including the torso's `rooty`, rotates about axis (0, −1, 0). This means a positive torso angle is a backward lean, and a positive hip angle moves the foot forward.
- The hip range is [−150°, 0°].

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 1.057, "phase0": 0.0, "feedback": {"obs[8]": 1.5}}],
 "couplings": [],
 "bias": {"a0": -0.25, "a3": -0.25, "a2": -0.075, "a5": -0.075},
 "units": [
  {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[10]": 0.08},
   "range": 1.5, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
  {"type": "reflex", "name": "swingR_A", "inputs": {"obs[8]": 1.3, "obs[1]": -4.0, "obs[2]": -4.0, "obs[10]": -0.5, "obs[11]": -0.5, "cos(P)": -0.119, "sin(P)": 1.194},
   "threshold": 1.452, "sharpness": 1.0, "to": {"a0": 0.5, "a3": -0.5}},
  {"type": "reflex", "name": "swingR_B", "inputs": {"obs[8]": -1.3, "obs[1]": 4.0, "obs[2]": 4.0, "obs[10]": 0.5, "obs[11]": 0.5, "cos(P)": -0.119, "sin(P)": 1.194},
   "threshold": 0.948, "sharpness": 1.0, "to": {"a0": -0.5, "a3": 0.5}},
  {"type": "reflex", "name": "swingL_A", "inputs": {"obs[8]": 1.3, "obs[1]": -4.0, "obs[5]": -4.0, "obs[10]": -0.5, "obs[14]": -0.5, "cos(P)": 0.119, "sin(P)": -1.194},
   "threshold": 1.452, "sharpness": 1.0, "to": {"a3": 0.5, "a0": -0.5}},
  {"type": "reflex", "name": "swingL_B", "inputs": {"obs[8]": -1.3, "obs[1]": 4.0, "obs[5]": 4.0, "obs[10]": 0.5, "obs[14]": 0.5, "cos(P)": 0.119, "sin(P)": -1.194},
   "threshold": 0.948, "sharpness": 1.0, "to": {"a3": -0.5, "a0": 0.5}},
  {"type": "linear", "name": "kneeR", "inputs": {"sin(P)": -1.146, "cos(P)": -0.355, "obs[3]": -1.5, "obs[12]": -0.2},
   "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
  {"type": "linear", "name": "kneeL", "inputs": {"sin(P)": 1.146, "cos(P)": 0.355, "obs[6]": -1.5, "obs[15]": -0.2},
   "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
  {"type": "linear", "name": "ankleR", "inputs": {"obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[13]": -0.03},
   "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
  {"type": "linear", "name": "ankleL", "inputs": {"obs[5]": -0.5, "obs[6]": -0.5, "obs[7]": -0.5, "obs[16]": -0.03},
   "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```