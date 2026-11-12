# Round 5: lower gains, a backward-leaning posture, thighs kept off their stop

## What the five results point to

**1. The feedback gains were high enough to make the hips chatter.** Walker2d's actuators have a gear ratio of 100, so an action of 1 is about 100 N·m.
- The torso's inertia about the hip is only about 0.2 kg·m².
- With both hips feeding back torso angular velocity, the effective damping per 8 ms step was 2 to 4 times the torso's inertia. That is past the point where discrete-time damping stays stable.
- This explains the 25–35% thigh saturation in rounds 3 and 4.
- The fix is to cut the damping gains by about 5 to 7 times and the stiffness gains by about 2 to 4 times. The new values are close to critical damping.

**2. The hips cannot flex forward.** Thigh angles are limited to 0 or below, so the torso can only be upright or leaning back relative to the legs.
- In rounds 1, 3 and 4 the target posture put the thighs at or near 0. Once the torso tipped back, positive hip torque only pressed the thighs into the stop and could not pitch the torso forward.
- The posture must keep the thighs in the middle of their range. That means the torso leans back slightly (equilibrium about −0.2 rad) and the stance thighs sit around −0.25.
- In this posture the foot can land about 0.15 rad ahead of the hip and sweep about 0.3 rad behind it. The mean leg angle is slightly behind vertical, which biases the walker forward.

**3. The ankle offsets lifted the toes and left the robot standing on its heels.** The ankle sits at the heel end of the foot, so a positive ankle bias tips the body back.
- The foot setpoint drops to a mild +0.05 rad.
- The foot gains are lowered so the foot no longer chatters during swing.

## Design

| Joint | Command |
|---|---|
| Thighs | 1.0·(θ_d − q) − 0.08·q̇ − 1.0·(torso + 0.15) − 0.07·ω − 0.1·v |
| Knees | 0.15 − 0.6·sin(φ + 0.5) − 0.03·q̇ |
| Feet | 1.0·(0.05 − q) − 0.03·q̇ |

- **Thighs:** the target is θ_d = −0.27 − 0.22·cos φ, which spans −0.49 to −0.05 rad. The thigh moves forward in swing (sin φ > 0) and backward in stance.
- **Torso lean and speed:** the −0.1·v term leans the torso back as forward speed rises. More lean lets the swing foot land further ahead, which brakes the walker.
- **Knees:** the knee starts to flex at toe-off and flexes most in early swing (about −0.45). It extends before touchdown and stays locked through stance.
- **Oscillators:** 1 Hz, in antiphase. R starts at π/2 and L at 3π/2, so both thigh targets begin equal. The first step is the right leg swinging while the left stands.

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
 "bias": {"a0": -0.42, "a3": -0.42, "a1": 0.15, "a4": 0.15, "a2": 0.05, "a5": 0.05},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"cos(R)": -0.22, "obs[2]": -1.0, "obs[11]": -0.08, "obs[1]": -1.0, "obs[10]": -0.07, "obs[8]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"cos(L)": -0.22, "obs[5]": -1.0, "obs[14]": -0.08, "obs[1]": -1.0, "obs[10]": -0.07, "obs[8]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"sin(R)": -0.53, "cos(R)": -0.29, "obs[12]": -0.03},
    "range": 1.2, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"sin(L)": -0.53, "cos(L)": -0.29, "obs[15]": -0.03},
    "range": 1.2, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```