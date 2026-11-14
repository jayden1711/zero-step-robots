Round 0 failed for one reason. At t = 0 both hips received a constant torque of about −0.5: the thigh-target offset plus the lean offset in the bias. With both feet down, that pitched the torso backward at about 5 rad/s. The torso feedback gain of 1.5 was far too weak to stop it, and the thigh units saturated half the time.

Changes for round 1:

- **Separate balance unit.** Torso balance now has its own unit, driving both hips: −3·(obs[1] + 0.2·obs[10]). This makes balance clearly stronger than the thigh tracking.
- **Weaker thigh tracking, near-zero starting torque.** The thigh PD is softer (Kp 1), with target −0.25 + 0.4·cos φ. The hip bias is now ≈ +0.05: the thigh offset (−0.25) is roughly cancelled by a small forward-lean setpoint (+0.1 rad × 3). There is no longer a large torque at the start.
- **Smaller knee flex.** The knee now flexes to −0.5 instead of −0.8, which limits the height drop and jolt at the start.
- **Wider ranges.** I raised the declared ranges so the units stop saturating.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.05, "a1": -0.5, "a2": 0.0, "a3": 0.05, "a4": -0.5, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
    "range": 2.0, "tol": 0.02, "to": {"a0": -3.0, "a3": -3.0}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.4, "obs[2]": -1.0, "obs[11]": -0.1},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.5, "obs[3]": -2.0, "obs[12]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.4, "obs[5]": -1.0, "obs[14]": -0.1},
    "range": 3.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.5, "obs[6]": -2.0, "obs[15]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```