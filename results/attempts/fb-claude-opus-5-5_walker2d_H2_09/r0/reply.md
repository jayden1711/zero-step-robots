Round-0 design: an antiphase CPG with PD-style joint tracking. Balance is handled by torso feedback at both hips, a gated knee flexion during swing, and compliant ankles. This round is partly a probe; the results will tell me what to tune.

- **Rhythm:** oscillators R and L run at 0.9 Hz, held π apart by symmetric coupling.
  - They start at +π/2 and −π/2, so one leg begins at the end of swing (thigh near 0, under the hip) and the other at the end of stance.
- **Thighs (a0, a3):** each is one linear unit that combines four terms:
  - **Joint stiffness:** Kp = 2 toward the target q* = −0.3 + 0.25·sin φ. The thigh angle rises during swing, when cos φ > 0, and falls during stance.
  - **Leg damping in the world frame:** −0.3·(q̇_thigh − obs[10]). This damps the swinging leg without adding much damping to the light torso.
  - **Torso feedback:** −1.0·obs[1] − 0.11·obs[10].
  - **Bias:** the target offset plus a torso lean target of −0.15 rad (slightly back), so feet can land a little ahead of the hip given the thigh range [−2.62, 0].
- **Knees (a1, a4):**
  - A PD unit holds each knee nearly straight (target −0.05).
  - A reflex unit adds about −1.2 of flexion torque in a phase window centred slightly before mid-swing, using cos(φ+0.4) > 0.3. The bias is set so the net flexion torque is zero in stance.
- **Feet (a2, a5):** soft PD toward 0.

The gains are kept small enough to stay stable with the 0.008 s zero-order hold, given the torso's small inertia (about 0.2 kg·m²).

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
 "bias": {"a0": -0.75, "a3": -0.75, "a1": -0.7, "a4": -0.7},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[2]": -2.0, "obs[11]": -0.3, "obs[10]": 0.19, "obs[1]": -1.0, "sin(R)": 0.5},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[5]": -2.0, "obs[14]": -0.3, "obs[10]": 0.19, "obs[1]": -1.0, "sin(L)": 0.5},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -2.0, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -2.0, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(R)": 0.921, "sin(R)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.6}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(L)": 0.921, "sin(L)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.6}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```