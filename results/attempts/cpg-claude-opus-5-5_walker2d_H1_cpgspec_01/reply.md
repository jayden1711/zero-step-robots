This is a single-oscillator antiphase walking controller. The design rests on my reading of the Walker2d model; I couldn't run anything to check it.

**Joint convention.** All joints rotate about the −y axis, so a positive angle swings a hanging limb forward (+x) and tips the torso backward.
- The thigh range is [−150°, 0], so the hip can only extend backward from vertical.
- The knee range is the same, which is ordinary human-like knee bending.
- The foot is a plate that extends forward from the ankle. A positive foot angle means toes up.

**Rhythm.** One oscillator `g` at 0.9 Hz drives both legs. The left leg uses the negated cos and sin terms, which is exactly a π phase shift, so no coupling is needed. Forward velocity speeds up the phase slightly (0.8 rad/s per m/s), so the robot steps faster when it moves faster.

**One unit per joint.** Each unit is a PD controller in the joint's own frame, with a target taken from the oscillator.
- **Thigh:** target = −0.2 + 0.22·cos φ. Stance runs from φ = 0 to π, with the thigh sweeping backward. Swing runs from π to 2π, with the thigh coming forward. Gains are Kp = 2 and Kd = 0.12.
- **Knee:** target = −0.45 − 0.45·cos(φ − 4.24). It is straight in mid-stance and bends to −0.9 early in the swing for ground clearance. Gains are Kp = 2 and Kd = 0.1.
- **Ankle:** a soft PD (Kp = 0.8) that roughly follows a flat-foot roll during stance, with toes slightly up during swing.

**Balance.** Both thigh units also add 1.0·(torso angle − 0.05) + 0.05·(torso angular velocity). On the stance leg, a positive hip torque pitches the torso forward, so this keeps the torso upright.

**Speed regulation.** Two mechanisms act around a target speed of 0.8 m/s:
- **Torso lean:** the torso reference angle rises with speed. A more backward lean moves swing-foot placement forward, which brakes the robot.
- **Ankle torque:** when the robot is too slow, the ankles apply a toes-up torque. This moves the centre of pressure toward the heel, so the body falls forward. When the robot is too fast, the ankles push toes down to brake.

**Start.** The initial phase is 0.75π. This begins the gait as a split stance: the right leg is late in stance and the left leg is about to land in front, so the first step forward comes almost immediately.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "g", "freq_hz": 0.9, "phase0": 2.356, "feedback": {"obs[8]": 0.8}}],
 "couplings": [],
 "bias": {"a0": -0.29, "a1": -0.9, "a2": 0.24, "a3": -0.29, "a4": -0.9, "a5": 0.24},
 "units": [
   {"type": "linear", "name": "right_thigh_pd_balance",
    "inputs": {"obs[2]": -2.0, "obs[11]": -0.12, "cos(g)": 0.44, "obs[1]": 1.0, "obs[10]": 0.05, "obs[8]": -0.2},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "left_thigh_pd_balance",
    "inputs": {"obs[5]": -2.0, "obs[14]": -0.12, "cos(g)": -0.44, "obs[1]": 1.0, "obs[10]": 0.05, "obs[8]": -0.2},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "right_knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.1, "cos(g)": 0.408, "sin(g)": 0.802},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "left_knee_pd",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.1, "cos(g)": -0.408, "sin(g)": -0.802},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "right_foot_pd_speed",
    "inputs": {"obs[4]": -0.8, "obs[13]": -0.03, "cos(g)": -0.12, "sin(g)": -0.08, "obs[8]": -0.3},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "left_foot_pd_speed",
    "inputs": {"obs[7]": -0.8, "obs[16]": -0.03, "cos(g)": 0.12, "sin(g)": 0.08, "obs[8]": -0.3},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```