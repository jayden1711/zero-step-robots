Round 1 was a mistake. Flipping the torso-feedback sign made things much worse: the robot fell in 0.05 s instead of 1.2 s.

**What the data shows**
- **Round 1, while airborne:** strong negative thigh torque swung both thighs back to −0.99. The torso pitched back to −0.88 at the same time.
- So negative hip torque lowers obs[1], as the task hint says. To correct a torso tilt, the thigh torque must oppose obs[1] and obs[10]. That is the round-0 sign.
- **Why round 0 fell:** both thighs sat at their 0 stop, which absorbed the corrective positive torque. The knees were bent about −0.5 with the feet flat.
- Bending a knee tilts the thigh's lower end forward. With a straight hip, that tips the torso backward, which matches the slow backward fall in round 0.
- **Consequence for the posture:** the hip and knee can only bend backward. The torso therefore has to lean slightly back so the legs can reach in front of the hip during stance.

**Changes**
- **Torso feedback:** the round-0 sign is back, with stronger damping: −1.0·(obs[1] + 0.2) − 0.4·obs[10]. The target torso angle is −0.2.
- **Thigh:** the target is −0.25 + 0.25·cos φ, so it ranges from 0 to −0.5, with Kp = 1.5 and Kd = 0.1.
  - Relative to vertical, the stance leg sweeps from about 0.2 rad in front to 0.3 rad behind.
  - The thighs now spend most of the cycle away from the 0 stop, so the corrective torque reaches the torso.
- **Knee:** the target is −0.25 + 0.55·sin φ, with Kp = 1.5.
  - In stance it is clipped straight at the joint limit, so the bend no longer pushes the torso back.
  - In swing it flexes to −0.8.
- **Unchanged:** the feet, the oscillators and the coupling.

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
 "bias": {"a0": -0.575, "a1": -0.375, "a2": 0.0, "a3": -0.575, "a4": -0.375, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.5, "obs[11]": -0.1, "cos(R)": 0.375, "obs[1]": -1.0, "obs[10]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.5, "obs[14]": -0.1, "cos(L)": 0.375, "obs[1]": -1.0, "obs[10]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```