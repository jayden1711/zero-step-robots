Round 2 flips the sign of the torso-balance feedback at the thighs. Round 0 and round 1 both fell the same way, so I think round 1's feedback was pushing the torso further over instead of catching it.

**Why the sign was wrong**
- **Shared joint axis:** in the Walker2d model, the torso's angle and the thigh joints rotate about the same axis.
- **Torque reaction:** with a foot planted, a torque +τ at the thigh puts −τ on the torso, about that same axis. So a positive thigh torque lowers obs[1], and a negative thigh torque raises it.
- **Round 1 data agrees:**
  - obs[1] went negative, so the old term −3·obs[1] gave a large positive thigh torque.
  - That torque drove obs[1] further negative. This is positive feedback.
  - That explains why stronger "balance" in round 1 only slowed the fall.
- **Thigh PD term:** with the leg fixed, a torso tilt θ changes the thigh angle by about −θ. So the term −Kp·obs[2] already adds +Kp·θ, which restores. The old −3θ outweighed it, leaving a net −1.5θ.

This reasoning conflicts with the design hint ("feedback opposes the sign of obs[1] at the stance thigh"). The data from both rounds supports the flip, so I'm following the data.

**Revisions**
- **Thigh balance is now +3.0·obs[1] + 0.5·obs[10].** With the PD term, the net restoring stiffness is about 4.5·θ.
- **Lean setpoint is 0 for now.** It's still unclear which sign of obs[1] means forward. Next round I'll set the lean from the measured speed.
- **Thigh target offset is smaller:** the target is −0.15 + 0.3·cos φ, so the thigh bias is −0.225. The PD and rhythm are unchanged at Kp = 1.5, Kd = 0.15.
- **Knee, foot and oscillators:** unchanged from round 1.

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
 "bias": {"a0": -0.225, "a1": -0.8, "a3": -0.225, "a4": -0.8},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": 3.0, "obs[10]": 0.5},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": 3.0, "obs[10]": 0.5},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.697, "cos(R)": 0.717, "obs[3]": -2.0, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.697, "cos(L)": 0.717, "obs[6]": -2.0, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```