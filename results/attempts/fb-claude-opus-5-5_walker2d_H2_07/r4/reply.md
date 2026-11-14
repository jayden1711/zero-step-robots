Round 4 drops the open-loop thigh rhythm. It drives only the swing hip forward and leaves the stance hip to balance the torso.

**What rounds 0 to 3 show**
- **The torso falls back every time.** In round 3 it reached −0.38 rad within 0.1 s. At that moment the left thigh's PD target was far behind it, so the left thigh torque sat at −1. A negative thigh torque pitches the torso backward, so the robot started falling before the first step.
- **The stance hip was fighting the torso.** All four rounds told the stance thigh to swing backward with a sizable negative torque. With the foot planted, that torque mostly rotates the light torso backward rather than moving the body forward. That fits the backward walking (−0.3 to −0.7 m/s) and the backward falls.
- **The thigh joint limit changes the target posture.** The thigh can't go past 0 (in line with the torso). The swing foot can only land ahead of the hip if the torso leans back a little. So I now aim for a slight backward lean instead of a forward one.

**Round 4 design**
- **Swing hip only:** a soft phase gate adds about 0 to +0.8 thigh torque during swing (sin φ < 0) and about 0 during stance. This swings the leg forward to the thigh limit. Nothing pushes the stance thigh backward; it trails behind as the body moves forward over the foot.
- **Torso balance on both thighs:** torque = −2.5·(obs[1] + 0.1 + 0.12·obs[10] + 0.05·obs[8]).
  - The torso settles near −0.1 rad, and leans back further at higher speed, which places the foot further ahead.
  - This is the stabilising sign confirmed in rounds 1 and 2.
- **Knee:** torque = 0.2 + 0.6·cos(φ − 0.6) − 0.1·knee velocity.
  - Through most of stance the torque is positive, holding the knee straight against its limit.
  - The knee flexes around liftoff (peak at φ ≈ 3.7) and extends again before touchdown.
- **Feet:** PD hold at 0, unchanged.
- **Rhythm:** 1.0 Hz, with the same antiphase coupling.

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
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.2, "a4": 0.2},
 "units": [
   {"type": "reflex", "name": "R_swing_drive", "inputs": {"sin(R)": -1.0}, "threshold": 0.0,
    "sharpness": 3.0, "to": {"a0": 0.4}},
   {"type": "reflex", "name": "L_swing_drive", "inputs": {"sin(L)": -1.0}, "threshold": 0.0,
    "sharpness": 3.0, "to": {"a3": 0.4}},
   {"type": "linear", "name": "torso_balance_speed", "inputs": {"obs[1]": 1.0, "obs[10]": 0.12, "obs[8]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a0": -2.5, "a3": -2.5}},
   {"type": "linear", "name": "R_knee", "inputs": {"cos(R)": 0.495, "sin(R)": 0.339, "obs[12]": -0.1},
    "range": 1.6, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee", "inputs": {"cos(L)": 0.495, "sin(L)": 0.339, "obs[15]": -0.1},
    "range": 1.6, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd", "inputs": {"obs[4]": 1.0, "obs[13]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "L_foot_pd", "inputs": {"obs[7]": 1.0, "obs[16]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```