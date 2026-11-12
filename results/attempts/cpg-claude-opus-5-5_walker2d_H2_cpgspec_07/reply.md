## Controller design: antiphase PD-tracking gait with torso balance

**Sign conventions.** The brief gives two statements that cannot both be true:
- "positive `obs[1]` = forward lean"
- "negative thigh torque, with the foot planted, pitches the torso backward"

The torso joint (`rooty`) and the hip use the same hinge axis. In joint coordinates, a hip torque τ acts on the torso as −τ. With the foot planted, a positive thigh torque therefore always *decreases* `obs[1]`, whichever direction counts as "forward."

So the stabilising feedback is thigh torque **+k·obs[1] + kd·obs[10]**, and I use that sign. Together with the knee and thigh angle conventions, this also implies that positive `obs[1]` means leaning *back*. That matters because the hips can only extend (angle ≤ 0). A slight backward lean is what lets the swing foot land ahead of the hip and brake.

**Rhythm.** Two oscillators run at 0.8 Hz.
- They are coupled with a lag of π, so the legs stay in antiphase.
- Forward speed feeds into both oscillators (1.5 rad/s per m/s). The legs step faster when the body speeds up, which keeps the feet under the body.

**Joints.** Each joint has one linear unit doing PD tracking, `Kp·(target(φ) − q) − Kd·q̇`. Each target's constant part goes into the action bias.
- **Thigh:** target is −0.25 + 0.3·cos(φ + 0.4). The 0.4 rad phase lead offsets the tracking lag of the swing leg. Kp = 1.5, Kd = 0.08.
- **Knee:** target is −0.45 + 0.85·sin(φ + 0.4).
  - During stance the target is positive, which presses the knee against its limit and keeps it straight.
  - Flexion starts at the end of stance and peaks early in swing, which clears the foot.
  - The knee is extended again just before touchdown.
- **Foot:** target is +0.1 (toes up relative to the shin). With the foot flat on the ground, this tilts the shin forward. The centre of mass then sits over the forefoot, which gives a gentle forward bias.

**Balance and speed.** Both thighs get torso feedback: 3·(θ − θ_ref) + 0.05·θ̇.
- The reference lean is θ_ref = 0.15 + 0.2·(v − 0.6).
- If the robot goes faster than about 0.6 m/s, it leans back more, so the feet land further ahead and slow it down.
- The thigh, torso-rate and torso-angle damping are kept small enough to avoid chatter, since the action is held for 8 ms per step.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 0.8, "feedback": {"obs[8]": 1.5}},
   {"name": "L", "freq_hz": 0.8, "phase0": 3.9416, "feedback": {"obs[8]": 1.5}}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.465, "a1": -0.675, "a2": 0.1, "a3": -0.465, "a4": -0.675, "a5": 0.1},
 "units": [
   {"type": "linear", "name": "thigh_R",
    "inputs": {"cos(R)": 0.414, "sin(R)": -0.175, "obs[2]": -1.5, "obs[11]": -0.08, "obs[1]": 3.0, "obs[10]": 0.05, "obs[8]": -0.6},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L",
    "inputs": {"cos(L)": 0.414, "sin(L)": -0.175, "obs[5]": -1.5, "obs[14]": -0.08, "obs[1]": 3.0, "obs[10]": 0.05, "obs[8]": -0.6},
    "range": 2.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 1.174, "cos(R)": 0.497, "obs[3]": -1.5, "obs[12]": -0.08},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 1.174, "cos(L)": 0.497, "obs[6]": -1.5, "obs[15]": -0.08},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "foot_R",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```