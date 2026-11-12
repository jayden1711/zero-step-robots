## Round 2 design: one shared torso torque plus a scissor term between the legs

**Why round 1 failed.** Round 1 made each thigh track its own leg-angle reference. During stance, driving the planted leg backward needs a negative hip torque, and that torque pitches the torso backward. So the leg-tracking error added to the torso balance term and shifted its equilibrium:

- The stance leg's tracking error reached about 0.5 rad.
- Divided by Kt = 1.5, that moves the torso equilibrium from −0.2 to about −0.55 rad.
- With both legs on the ground, both hips pulled the same way.

This matches the torso angles of −0.7 to −0.9 rad and the backward drift.

**Fix.** The torso pitch torque equals τ_R + τ_L, because each hip's reaction torque acts on the torso. I split the two hip torques into a common part and a differential part. This needs no stance/swing gating.

- **Torso balance (common mode).** τ_torso = −3(θ − θref) − 0.16·θ̇, with θref = −0.2. Half goes to each hip. This is the only net torque on the torso.
  - At about 40 rad/s on a torso of roughly 0.19 kg·m², damping is close to critical.
  - The −0.2 rad backward lean is still needed, because q ≤ 0 means a foot can only land ahead of the hip by about −θ.
- **Scissor (differential mode).** A torque of +K(δref − δ) − D·δ̇ goes to the right hip and the opposite to the left, with δ = q_R − q_L and δref = 0.5·cos φ_R.
  - θ cancels out of δ.
  - Because the two parts cancel, this term puts zero net torque on the torso.
  - With the stance foot planted, it swings the swing leg forward relative to the stance leg.
  - Gains: K = 1.5, D = 0.2.
- **Knee.** A stiff PD holds the knee straight. A phase reflex adds strong flexion during swing (sin φ < −0.3).
  - In swing the total knee torque is about −1.0, settling near −0.67 rad.
  - In stance it is about +0.2, pressing the knee against its straight limit for support.
- **Feet and phases.** The feet keep the same PD. The starting phases stay at π/2 and 3π/2, where δref = 0 matches the initial pose.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.3, "a1": -0.4, "a2": 0.0, "a3": -0.3, "a4": -0.4, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_common",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.16},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": 0.5}},
   {"type": "linear", "name": "hip_scissor_diff",
    "inputs": {"cos(R)": 0.375, "cos(L)": -0.375, "obs[2]": -1.5, "obs[5]": 1.5, "obs[11]": -0.2, "obs[14]": 0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"sin(R)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a1": -0.6}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"sin(L)": -1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a4": -0.6}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```