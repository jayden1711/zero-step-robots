The controller below has not been run, so its score is unknown. A rhythmic walking pattern is tracked by joint-angle servos, with balance and speed feedback added on top.

**How the joints move (my reading of the Walker2d model).** All joints rotate about the −y axis. A positive angle swings the foot forward, and a positive foot angle lifts the toe. The thigh and knee can only move between −150° and 0°. With the torso upright, a leg can therefore reach straight down at most. The feet point forward (+x), so the robot is supported between heel and toe.

**Rhythm.** There are two 1.0 Hz oscillators, R and L, held π apart by mutual coupling. Each leg's phase φ maps to target joint angles:

| Joint | Target | Behaviour |
|---|---|---|
| Thigh | −0.25 + 0.3·cos φ | φ = 0…π is stance, sweeping from +0.05 to −0.55. φ = π…2π is swing, returning forward. |
| Knee | −0.35 + 0.45·sin(φ+0.3) | Straight in mid-stance (pressed against its limit). Bent about −0.8 in mid-swing for ground clearance. |
| Ankle | Keeps the foot about 60% level with the ground | Adds a toe-down push near the end of stance (φ ≈ 0.8π) and lifts the toe just before touchdown. |

**Servos.** Each joint is one linear unit acting as a position servo: gain × (target − angle) − damping × joint velocity. The thigh and knee also get a velocity feed-forward term derived from the target's cos/sin, to reduce tracking lag. Gains are 1.8 / 0.15 for the thigh, 1.5 / 0.1 for the knee and 0.6 / 0.03 for the ankle. The damping values were chosen to keep the 8 ms control step numerically stable.

**Balance and speed.** Both thigh torques include +1.0 × (obs[1] − θd).
- This sign holds whichever way the axis convention runs, because the thigh and torso share the same rotation axis.
- The desired lean is θd = 0.05 + 0.25·(v − 0.6), where v is forward speed. When slow, the torso leans forward and the legs trail, so the robot tips forward. When fast, it leans back so the feet land ahead and brake.
- The constant parts of the servo and balance terms go into the action biases.

**Starting phases.** R starts at mid-stance (π/2) and L at mid-swing (3π/2), so the first step lifts L from the standing pose.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.35, "a1": -0.525, "a2": 0.0, "a3": -0.35, "a4": -0.525, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_servo_balance",
    "inputs": {"cos(R)": 0.54, "sin(R)": -0.283, "obs[2]": -1.8, "obs[11]": -0.15, "obs[1]": 1.0, "obs[8]": -0.25},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_servo",
    "inputs": {"cos(R)": 0.47, "sin(R)": 0.561, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_ankle_servo_pushoff",
    "inputs": {"obs[1]": -0.36, "obs[2]": -0.36, "obs[3]": -0.36, "obs[4]": -0.6, "obs[13]": -0.03, "cos(R)": 0.243, "sin(R)": -0.177},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_servo_balance",
    "inputs": {"cos(L)": 0.54, "sin(L)": -0.283, "obs[5]": -1.8, "obs[14]": -0.15, "obs[1]": 1.0, "obs[8]": -0.25},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_servo",
    "inputs": {"cos(L)": 0.47, "sin(L)": 0.561, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_ankle_servo_pushoff",
    "inputs": {"obs[1]": -0.36, "obs[5]": -0.36, "obs[6]": -0.36, "obs[7]": -0.6, "obs[16]": -0.03, "cos(L)": 0.243, "sin(L)": -0.177},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```