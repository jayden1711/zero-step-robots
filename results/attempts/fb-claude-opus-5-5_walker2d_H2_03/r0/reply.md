This first design is a two-oscillator antiphase walking gait. Each joint is held by a PD servo around a rhythmic target, and torso balance feedback is added to both hips.

**Oscillators**
- Two oscillators, R and L, run at 1.0 Hz.
- They are coupled both ways with weight 2.0 and a lag of π, so they settle half a cycle apart.

**Phase plan per leg**
- **Stance (φ from 0 to π):** the thigh swings back, and the knee straightens to about 0 at φ = π/2.
- **Swing (φ from π to 2π):** the knee flexes to about −0.7 to clear the ground, and the thigh swings forward.

**Thigh (a0, a3)**
- The thigh tracks a target of −0.25 + 0.3·cos φ relative to the torso, with gains Kp = 1.0 and Kd = 0.1.
- Balance feedback is added to both thighs: −0.8·(torso angle − 0.2) − 0.1·(torso angular velocity).
- This holds a forward lean of about 0.2 rad. With that lean, the stance leg sweeps from about +0.25 to −0.35 rad from vertical, even though the hip can only bend backward.

**Knee (a1, a4)**
- The knee tracks −0.3 + 0.4·sin φ, with Kp = 1.5 and Kd = 0.1.

**Foot (a2, a5)**
- The foot holds a target of 0, with Kp = 1.0 and Kd = 0.05.

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
 "bias": {"a0": -0.09, "a1": -0.45, "a2": 0.0, "a3": -0.09, "a4": -0.45, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.1, "cos(R)": 0.3, "obs[1]": -0.8, "obs[10]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.6},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.1, "cos(L)": 0.3, "obs[1]": -0.8, "obs[10]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.6},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```