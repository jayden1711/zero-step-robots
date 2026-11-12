The torso pitched back within 0.1 s again (−0.26 rad) and the robot walked backward.

**Why it keeps falling backward.** The leg's angle from vertical is roughly the thigh angle minus the torso angle. The thighs cannot go past 0, so pitching the torso forward against still feet needs room for the thigh angle to rise toward 0. Once the torso leans back with the feet in front, it cannot recover: the thighs hit their stop, as in round 1. In rounds 0 and 2 the large negative thigh bias pitched the torso back at once. With the feet in front of the centre of mass, the robot then rolled backward.

The robot must never get into a back-lean with its feet in front. Instead it should start by tipping slightly forward over its feet, and place its feet in front only when it is moving forward.

**Changes for round 3**
- **Thighs:** a PD controller tracks a target of −0.25 − 0.25·cos φ, which spans −0.5 to 0 rad. Gains are Kp 1 and Kd 0.1.
  - Torso feedback is stronger: −4·(torso angle − θ*) − 0.5·(torso angular velocity).
  - The lean setpoint is θ* = 0.05 − 0.15·(forward speed). When the robot speeds up, the torso leans back, which lets the swing foot land further forward and brakes it.
  - No extra bias, so the net thigh torque at start is about −0.05 instead of saturating at −1.
- **Ankles (feet):** the PD setpoint is now +0.1 rad (bias +0.2). A positive ankle torque with the foot planted tips the leg, and so the body, forward. This gives a gentle forward lean over the feet.
- **Start phases:** R starts at π/2 (mid-swing) and L at 3π/2 (mid-stance). At the start the thigh rhythm terms are zero, and the robot begins by lifting its right knee while standing on the left leg.
- **Knees:** unchanged from round 2.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.05, "a3": -0.05, "a1": 0.2, "a4": 0.2, "a2": 0.2, "a5": 0.2},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"cos(R)": -0.25, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -4.0, "obs[10]": -0.5, "obs[8]": -0.6},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"cos(L)": -0.25, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -4.0, "obs[10]": -0.5, "obs[8]": -0.6},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"sin(R)": -0.5, "cos(R)": -0.4, "obs[12]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"sin(L)": -0.5, "cos(L)": -0.4, "obs[15]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -2.0, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -2.0, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```