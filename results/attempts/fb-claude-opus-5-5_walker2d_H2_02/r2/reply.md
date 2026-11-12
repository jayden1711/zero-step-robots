## Round 2 design

### What went wrong in rounds 0 and 1

**1. The derivative gains made the hips chatter.** Each action unit is about 100 N·m of torque. The torso's inertia about the hip is only about 0.2 kg·m², and one step is 0.008 s. The torso damping I summed over both hips was 1.4 action-units·s in round 1 and 0.7 in round 0. Either way, damping × dt / inertia was far above 2, so each step overshot the last. This explains why the thigh actions sat at ±1 for 55–83% of steps.

**2. The thigh joint limit at 0 made balance impossible.** A thigh angle can only go from 0 down to −2.62, so relative to the torso the leg can only swing backward. In round 1 both thighs were pushed against the 0 limit, at +0.04. The torso and legs then fell backward together as one rigid stick, and hip torque could not separate them.

**3. The torso has to lean back for the feet to reach forward.** The data fits the thigh's tilt from vertical being (torso angle − thigh angle). For example, in round 0 the torso was at −0.7 and the thigh at −0.66, so the legs were near vertical. This means a foot can only be placed ahead of the hip if the torso leans back. The torso is light, about 3.5 kg of 23 kg, so a backward lean of about 0.2 rad barely moves the centre of mass.

### Changes for round 2

**Torso.** The torso target is now −0.2 rad. Torso stiffness is 1 per hip. Torso damping is 0.03 per hip, plus the thigh damping, which stays below the stability limit.

**Thighs.**
- The target is −0.25 + 0.25·cos φ, which keeps the thigh in [−0.5, 0] and off the limit except at touchdown.
- The thigh tilt runs from about −0.2 (foot ahead) to +0.3 (foot behind).
- Kp is 1.5 and Kd is 0.08.

**Knees.**
- The target is −0.2 + 0.4·sin(φ + 0.3).
- During stance the knee stays straight, pressed into its limit.
- During swing it flexes to −0.6, with the peak flexion moved earlier in the swing for ground clearance.

**Ankles.** A soft PD hold: Kp 0.5 and Kd 0.03. The damping is kept below the light foot's stability limit.

**Frequency.** 0.9 Hz.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.575, "a1": -0.4, "a2": 0.0, "a3": -0.575, "a4": -0.4, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.03},
    "range": 1.5, "tol": 0.02, "to": {"a0": -1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.375, "obs[2]": -1.5, "obs[11]": -0.08},
    "range": 2.5, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.764, "cos(R)": 0.236, "obs[3]": -2.0, "obs[12]": -0.1},
    "range": 3.5, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.375, "obs[5]": -1.5, "obs[14]": -0.08},
    "range": 2.5, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.764, "cos(L)": 0.236, "obs[6]": -2.0, "obs[15]": -0.1},
    "range": 3.5, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```