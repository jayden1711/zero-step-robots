# Round 1: switching to the brief's sign convention for torso balance

**What round 0 showed.** In the first 0.1 s the torso swung to about −0.3 and then stayed near −0.45 while the robot drifted backwards at −0.4 m/s. That fits the brief's convention, where negative obs[1] means a backward lean and a negative thigh torque pitches the torso back. It does not fit my joint-axis reading. The hips also saturated for about 70% of steps because the large negative bias kept pressing the thighs back.

**Changes in this design:**
1. **Balance sign.** I now use the brief's convention. The hip balance term is −Kb·(obs[1] − θ₀) − Kbd·obs[10], with Kb = 1.5 and Kbd = 0.15. The leg's forward angle relative to vertical is taken as obs[2] − obs[1]. With that reading, round 0's −0.45 lean plus thighs near −0.25 put the feet ahead of the hip while leaning back, which explains the backward drift.
2. **Hip tracking in joint space.** Each thigh tracks −0.225 + 0.225·cos φ, so it stays inside the joint limit (between −0.45 and 0). Kp is lowered to 1.0 and Kd is 0.1. The constant bias is smaller (−0.19 instead of −0.365), and the declared range is wider so the unit saturates less.
3. **Lean target and speed control.** The lean target is θ₀ = 0.025 − 0.15·obs[8], about −0.05 at 0.5 m/s. A slight backward lean lets the swing foot land in front of the hip. Going faster gives a negative hip torque, which pitches the torso back and slows the robot.
4. **Knee timing.** Each knee tracks −0.3 + 0.5·sin(φ + 0.4), with Kp = 1.5. The knee is straight through stance and flexes most early in the swing.
5. **Frequency.** Raised from 0.8 Hz to 1.0 Hz.
6. **Ankles.** Slightly stiffer.

**What to test.** If the torso now falls forward and the robot runs off, the lean offset is the next thing to tune. If the torso still drifts negative, the hip bias is.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.19, "a1": -0.45, "a3": -0.19, "a4": -0.45},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.225, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -1.5, "obs[10]": -0.15, "obs[8]": -0.225},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.69, "cos(R)": 0.29, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.225, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -1.5, "obs[10]": -0.15, "obs[8]": -0.225},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.69, "cos(L)": 0.29, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```