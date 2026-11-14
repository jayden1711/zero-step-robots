Round 3 replaces open-loop torques with joint-space PD tracking of phase-dependent targets. I expect this to fix the backward walking.

**What rounds 0 to 2 show**
- **Your sign convention is right.** In round 1 both the torso angle and the thigh angle went negative in mid-air, before either foot touched down. Only your convention conserves angular momentum in that motion. That confirms that −obs[1] at the thighs is the stabilising sign.
- **Why the robot walked backward:** with open-loop torques, the thigh lags its torque by about 90°. In round 2 each foot stayed on the ground until φ ≈ 3.2, which is well into the forward-swing half of the cycle. So the stance leg was swinging forward with its foot planted, pushing the body backward. The thighs were also at the action limit about half the time.

**Round 3 changes**
- **PD tracking at every thigh and knee:** each torque is Kp·(target(φ) − q) − Kd·q̇, built as one linear unit per joint. The rhythm constants (Kp × offset) go into the bias.
  - **Stance is φ ∈ (0, π), swing is φ ∈ (π, 2π).**
  - **Thigh target:** −0.35 + 0.3·cos(φ + 0.3), so most forward just before touchdown. Kp = 2.5, Kd = 0.3.
  - **Knee target:** −0.5 − 0.7·cos(φ − 4.0). The knee is straight from touchdown through mid-stance, starts flexing before liftoff, and peaks at about −1.2 in mid-swing. Kp = 4, Kd = 0.2.
- **Why PD also helps balance:** with the stance foot planted, tracking the thigh angle relative to the torso already resists torso pitch, with the stabilising sign.
- **Balance unit:** −1.0·obs[1] − 0.15·obs[10] − 0.05·obs[8], plus a small +0.05 thigh bias against the backward drift seen in every round so far.
- **Feet:** PD hold at 0 (Kp = 1, Kd = 0.05).
- **Frequency:** 0.9 Hz, with the same antiphase coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.825, "a3": -0.825, "a1": -2.0, "a4": -2.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd", "inputs": {"cos(R)": 0.716, "sin(R)": -0.222, "obs[2]": -2.5, "obs[11]": -0.3},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd", "inputs": {"cos(R)": 1.83, "sin(R)": 2.12, "obs[3]": -4.0, "obs[12]": -0.2},
    "range": 6.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_thigh_pd", "inputs": {"cos(L)": 0.716, "sin(L)": -0.222, "obs[5]": -2.5, "obs[14]": -0.3},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd", "inputs": {"cos(L)": 1.83, "sin(L)": 2.12, "obs[6]": -4.0, "obs[15]": -0.2},
    "range": 6.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "torso_balance_speed", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15, "obs[8]": 0.05},
    "range": 2.5, "tol": 0.05, "to": {"a0": -1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_foot_pd", "inputs": {"obs[4]": 1.0, "obs[13]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "L_foot_pd", "inputs": {"obs[7]": 1.0, "obs[16]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```