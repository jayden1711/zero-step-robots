The controller below is untested, since I can't run the simulation. It is a single-rhythm hopping gait with posture servoing on every joint, torso balance through the hip, and speed control through how far the torso leans.

**Rhythm.** One oscillator runs at 2.2 Hz and moves each joint's target angle.
- **Rising half (push-off):** the knee straightens (a1 up), the toe presses down (a2 down) and the thigh drives backward.
- **Falling half (flight):** the knee folds, the toe lifts and the thigh swings the leg forward.
- **Joint targets:**
  - knee: −0.35 + 0.25·sin φ
  - foot: 0.5 − 0.25·sin φ
  - thigh: −0.1 − 0.1·sin φ
- **Servo gains:** the knee servo gives 300 Nm/rad and the foot servo 200 Nm/rad. With the joint armature, that puts the leg's own bounce near the hop frequency, so the body should lock onto the rhythm.

**Balance.** Positive thigh torque pitches the torso forward when the foot is on the ground. So the hip receives +1.2·torso angle + 0.15·torso angular velocity. The thigh servo adds stiffness with the same sign during stance, giving roughly critically damped torso control.

**Speed.** The target lean is 0.15·(vx − 0.7). Standing still, the torso aims for a lean of about −0.1 rad (forward), which tilts the leg backward so each push drives forward. Above 0.7 m/s the target lean moves backward, which brings the leg forward and brakes. The speed term saturates beyond about ±2 m/s, keeping the target lean well inside the ±0.2 rad limit.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.2, "phase0": -1.5708}],
 "couplings": [],
 "bias": {"a0": 0.066, "a1": -0.525, "a2": 0.5},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.2, "obs[7]": 0.15},
    "range": 1.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "speed_lean", "inputs": {"obs[5]": -0.18},
    "range": 0.4, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd_rhythm", "inputs": {"obs[2]": -0.6, "obs[8]": -0.06, "sin(hop)": -0.06},
    "range": 1.2, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -1.5, "obs[9]": -0.12, "sin(hop)": 0.375},
    "range": 2.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd_rhythm", "inputs": {"obs[4]": -1.0, "obs[10]": -0.08, "sin(hop)": -0.25},
    "range": 1.8, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```