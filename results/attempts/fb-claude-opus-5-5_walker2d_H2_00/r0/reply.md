This first design is a PD-tracking CPG gait with torso balance feedback.

**Structure**
- **Oscillators.** Two oscillators, R and L, run at 0.9 Hz. They are coupled both ways with a lag of π, so the legs settle in antiphase. R starts at phase 0 and L at π.
- **Stance and swing.** Each leg is in stance while φ ∈ [0, π] and in swing while φ ∈ [π, 2π].
- **Joint tracking.** Each joint has one linear unit that acts as a PD controller following a sinusoidal reference. The torque is Kp·(ref(φ) − q) − Kd·q̇, and the constant part Kp·offset goes into `bias`. The references are:
  - Thigh: q_ref = −0.25 + 0.25·cos φ. It goes from 0 (forward) to −0.5 (back) during stance and returns during swing. Kp = 2, Kd = 0.4.
  - Knee: q_ref = −0.4 + 0.4·sin φ. The knee is straight at mid-stance and flexed to −0.8 at mid-swing, for ground clearance. Kp = 2, Kd = 0.15.
  - Foot: q_ref = 0. Kp = 1, Kd = 0.03. The foot stays roughly flat and pushes off passively as the stance leg extends back.
- **Torso balance.** Both thigh units also receive −1.0·obs[1] − 0.1·obs[10]. A negative hip torque pitches the torso backward, so this term opposes forward lean and forward pitch rate. In stance, the joint-space thigh PD also helps keep the torso upright.
- **Scale.** Gains are in action units, so 1 = 100 Nm. They are sized against the estimated segment inertias, roughly 3.7 kg·m² for a whole leg about the hip, to stay moderately damped.

**What I will watch for in the results**
- The sign of obs[1].
- Whether the robot falls forward or backward.
- Whether it walks in place.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.5, "a1": -0.8, "a2": 0.0, "a3": -0.5, "a4": -0.8, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.5, "obs[2]": -2.0, "obs[11]": -0.4, "obs[1]": -1.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.8, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.5, "obs[5]": -2.0, "obs[14]": -0.4, "obs[1]": -1.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.8, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```