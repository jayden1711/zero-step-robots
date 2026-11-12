Round 0 is a first-principles CPG walker. I haven't tuned it, so I'm using it partly to see how the robot responds.

**Structure**
- **Oscillators:** two, R and L, at 1.0 Hz. They are coupled both ways with a lag of π, so the legs settle in antiphase. R starts at 0 and L starts at π.
- **Thighs (a0, a3):** a PD controller tracks a rhythmic target, θ_d = −0.3 − 0.3·cos φ. That target lies between −0.6 and 0 rad, inside the joint range [−2.62, 0].
  - The target moves forward when sin φ > 0 (swing) and backward when sin φ < 0 (stance).
  - Gains are Kp = 2 and Kd = 0.2.
  - Balance feedback is added: −2·(torso angle − 0.05) − 0.3·(torso angular velocity). A negative thigh torque pitches the torso back, so this opposes forward lean, with a small 0.05 rad forward-lean setpoint for propulsion.
- **Knees (a1, a4):** the torque is 0.3 − 0.6·(sin φ + cos φ), plus damping. This flexes the knee around early-to-mid swing (φ ≈ π/4) to clear the ground, and holds it extended against the 0 limit during stance.
- **Feet (a2, a5):** a PD controller holds each foot near neutral.

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
 "bias": {"a0": -0.5, "a3": -0.5, "a1": 0.3, "a4": 0.3},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"cos(R)": -0.6, "obs[2]": -2.0, "obs[11]": -0.2, "obs[1]": -2.0, "obs[10]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"cos(L)": -0.6, "obs[5]": -2.0, "obs[14]": -0.2, "obs[1]": -2.0, "obs[10]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"sin(R)": -0.6, "cos(R)": -0.6, "obs[12]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"sin(L)": -0.6, "cos(L)": -0.6, "obs[15]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```