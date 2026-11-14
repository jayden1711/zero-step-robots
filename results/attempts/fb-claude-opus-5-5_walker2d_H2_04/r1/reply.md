Round 0 fell backward in about 0.1 s, before any gait started. I think there were two causes:

- **Thigh bias:** both thighs started with a −0.5 bias torque. When the feet touched down, the reaction pitched the torso backward. The balance gain of 1.0 was too weak to fight the PD term and the bias, so both thigh units saturated.
- **Left knee:** at φ = 3π/2 its command came out near −2.75, clipped to −1. The knee collapsed at the start.

**Revisions**
- **Thigh balance is now dominant:** −3.0·(obs[1] − 0.1) − 0.6·obs[10].
  - The rhythmic PD is weaker: Kp = 1.5, Kd = 0.15.
  - The thigh target is −0.25 + 0.3·cos φ.
  - The net bias is nearly zero: −0.375 + 0.3 = −0.075.
- **Knee:**
  - The target is −0.4 + 0.5·sin(φ + 0.8), giving 0.697·sin φ + 0.717·cos φ.
  - The PD term is Kp = 2, Kd = 0.1, with bias −0.8, so the knee stays near straight in stance.
- **Frequency:** slightly faster, at 0.9 Hz.
- **Unit ranges:** widened so the balance term stays linear over its useful range.

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
 "bias": {"a0": -0.075, "a1": -0.8, "a3": -0.075, "a4": -0.8},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"cos(R)": 0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -3.0, "obs[10]": -0.6},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"cos(L)": 0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -3.0, "obs[10]": -0.6},
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