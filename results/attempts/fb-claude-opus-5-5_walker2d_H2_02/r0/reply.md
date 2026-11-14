This first design uses PD tracking of rhythmic joint targets driven by two antiphase oscillators, plus torso balance feedback on the hips.

**Oscillators.** There are two, R and L, at 1 Hz. They are coupled both ways with lag π, so they lock in antiphase. With phase φ, stance is φ ∈ (0, π), where the thigh sweeps backward. Swing is φ ∈ (π, 2π), where the thigh comes forward and the knee flexes.

**Joint targets, per leg.** Each joint is one linear unit computing Kp·(target − q) − Kd·q̇. The constant part of each target goes into the bias.
- **Thigh:** the target is −0.3 + 0.3·cos φ, which spans the hip's allowed range of [−0.6, 0]. Kp is 1.5 and Kd is 0.15. Torso feedback of −1.5·obs[1] − 0.2·obs[10] is added, so a forward lean produces negative hip torque, which pitches the torso back. The bias holds a slight backward torso lean of about −0.05 rad, so the swing foot can reach a little ahead of the hip.
- **Knee:** the target is −0.4 + 0.4·sin φ. That is 0 (straight, at the joint limit) at mid-stance and −0.8 at mid-swing, for ground clearance. Kp is 2 and Kd is 0.15.
- **Ankle:** a PD hold at 0, with Kp 1 and Kd 0.1.

**Start.** The right leg starts at mid-stance (φ = π/2) and the left at mid-swing (φ = 3π/2). At those phases both thigh targets are −0.3, which avoids a jolt at t = 0.

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
 "bias": {"a0": -0.525, "a1": -0.8, "a2": 0.0, "a3": -0.525, "a4": -0.8, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.8, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -1.5, "obs[10]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.8, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```