## Round 2 design

### What went wrong in round 1

The torso still settled about 0.4 rad backward, and the robot again walked backward until it fell.

The cause was in how the thigh gains combined:

- The world-frame leg term added +Kp·obs[1] to each thigh command. That cancelled half of the torso stiffness, leaving a net gain of only −1.5.
- The constant lean bias of −0.6 then set the equilibrium at about −0.6 / 1.5 = −0.4 rad. That matches the measured lean.
- Leaning that far back puts the centre of mass behind the feet. The robot therefore drifted backward.
- The deep crouch at the end (height too low) came from the knees giving way while leaning back.

### Changes in round 2

- **Torso stiffness now dominates.**
  - Kt = 3 and Kp = 1, so the net obs[1] gain at each thigh is −2.
  - Torso damping is Kdt = 0.1 and leg damping Kd = 0.15, so the obs[10] coefficient is +0.05.
- **The lean target is almost upright (−0.05 rad).**
  - The leg target is now φ_w* = −0.1 + 0.3·sin φ in the world frame, so each leg is slightly behind the hip on average.
  - The bias is Kt·lean + Kp·φ0 = −0.15 − 0.1 = −0.25, much smaller than before.
- **Speed feedback is added: −0.15·obs[8] at each thigh.**
  - When the robot moves backward, the torso is commanded to lean forward, and the reverse when it moves forward.
  - This acts as lean = l0 − 0.05·v.
- **The knees are stiffer.**
  - The PD gain is 3, the damping 0.15, and the bias is −0.65.
  - With these values the stance knee holds near straight, with a net offset of about −0.05.
  - The swing flexion is a little stronger, at −0.7.
- **Oscillators and feet are unchanged.**

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.5708}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.1416},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.1416}
 ],
 "bias": {"a0": -0.25, "a3": -0.25, "a1": -0.65, "a4": -0.65},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[1]": -2.0, "obs[2]": -1.0, "obs[10]": 0.05, "obs[11]": -0.15, "obs[8]": -0.15, "sin(R)": 0.3},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[1]": -2.0, "obs[5]": -1.0, "obs[10]": 0.05, "obs[14]": -0.15, "obs[8]": -0.15, "sin(L)": 0.3},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -3.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -3.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.7}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.7}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```