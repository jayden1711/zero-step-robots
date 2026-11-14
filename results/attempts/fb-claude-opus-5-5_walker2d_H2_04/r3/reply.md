Round 2 got much worse: the walker fell in 0.05 s, about 20 times faster than round 1. So my sign flip was wrong; it made the torso feedback strongly destabilising, as the design hint warned. Round 3 goes back to the hint's sign and fixes what was actually weak in round 1.

**What really went wrong in round 1**
- With a foot planted, a backward torso tilt θ < 0 raises that thigh's joint angle by about |θ|.
- The thigh PD term (−1.5·obs[2]) then gives a negative torque, which pitches the torso further back.
- So the PD term worked against the balance term. The net restoring gain was only about 3 − 1.5 = 1.5, too weak, and the torso slowly tipped back over about 1 s.

**Revisions**
- **Separate balance unit:** −5.0·obs[1] − 0.9·obs[10], applied to both thighs.
  - It has its own unit, so the rhythmic PD can't saturate it.
- **Weaker thigh rhythm:** Kp = 1.0, Kd = 0.1. The target is −0.25 + 0.3·cos φ.
  - The PD now destabilises the torso by only about 1·θ, so the net restoring gain is about 4.
- **Forward lean setpoint of 0.15 rad,** to give forward drive. The thigh bias is 1.0·(−0.25) + 5·0.15 = 0.5.
- **Knee:** same target as before, but the bias is −0.6 so the knees squat less at the start.
- **Start phases:** 0 and π, so the left knee command doesn't start clipped at −1.
- **Foot and coupling:** unchanged.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.5, "a1": -0.6, "a3": 0.5, "a4": -0.6},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": -5.0, "obs[10]": -0.9},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.3, "obs[2]": -1.0, "obs[11]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.3, "obs[5]": -1.0, "obs[14]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
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