The design is a two-oscillator antiphase gait with joint-level PD tracking and torso balance through the hips. I couldn't test it, so some of the reasoning below rests on recalled model details.

**Sign conventions.** These are worked out from the `0 -1 0` joint axes and from my recollection of the MuJoCo model, which I couldn't check.
- A positive torso angle leans the torso back.
- A positive thigh angle moves the foot forward.
- A negative knee angle is normal flexion; the knee's upper limit is 0, which is straight.
- I recall the thigh range as [-150°, 0]. So each hip only swings the leg between −0.5 and 0 relative to the torso. The torso leans back about 0.15–0.35 rad, which lets the swing foot land ahead of the hip.

**Oscillators.** There is one oscillator per leg at 0.9 Hz, coupled so they stay π apart.
- They start at −π/2 (right leg in mid-stance) and +π/2 (left leg in mid-swing). This lets the robot start on one straight leg instead of in a double-support transient.
- For phase φ, the hip target is q = −0.25 − 0.25·cos φ. The thigh swings forward while sin φ > 0 and backward during stance.

**Hips (one linear unit each).** Each hip gets:
- A PD term toward the target, with gains kp = 1.5 and kd = 0.1.
- A torso PD term, with gain 3.5 on the angle and 0.02 on the angular velocity. This always acts in the right direction because the torso and thigh share the same joint axis.
- A desired torso lean that depends on speed: θd = 0.25 + 0.15·(v − 0.7). If the robot goes too fast, it leans back, which places the swing foot further ahead and slows it down. If it goes too slow, the reverse happens.
- The damping is deliberately small. The torso weighs only about 3.7 kg, so its rotational inertia is only about 0.24 kg·m². Large velocity gains would be numerically unstable at 0.008 s per step.

**Knees.**
- A PD unit with gain 2 targets a straight knee.
- A reflex flexes the knee by about 1 rad during swing. It is active while sin(φ + 0.5) > 0.35, which starts it slightly before swing begins and releases it well before the foot lands.
- During stance a +0.1 bias holds the knee locked against its straight limit.

**Feet.** The PD targets keep each foot level with the ground: target = −(torso + thigh + knee).
- During swing this keeps the toe from catching the ground.
- During stance, with the foot flat, it gives zero torque, so the ankle acts as a passive pivot.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": -1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 1.5708}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.8825, "a1": -0.9, "a3": -0.8825, "a4": -0.9},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"obs[2]": -1.5, "obs[11]": -0.1, "obs[1]": 3.5, "obs[10]": 0.02, "obs[8]": -0.525, "cos(R)": -0.375},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"obs[5]": -1.5, "obs[14]": -0.1, "obs[1]": 3.5, "obs[10]": 0.02, "obs[8]": -0.525, "cos(L)": -0.375},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_pd_R",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_pd_L",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R",
    "inputs": {"sin(R)": 0.878, "cos(R)": 0.479},
    "threshold": 0.35, "sharpness": 8.0, "to": {"a1": -1.0}},
   {"type": "reflex", "name": "knee_flex_L",
    "inputs": {"sin(L)": 0.878, "cos(L)": 0.479},
    "threshold": 0.35, "sharpness": 8.0, "to": {"a4": -1.0}},
   {"type": "linear", "name": "foot_level_R",
    "inputs": {"obs[1]": -1.0, "obs[2]": -1.0, "obs[3]": -1.0, "obs[4]": -1.0, "obs[13]": -0.04},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_level_L",
    "inputs": {"obs[1]": -1.0, "obs[5]": -1.0, "obs[6]": -1.0, "obs[7]": -1.0, "obs[16]": -0.04},
    "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```