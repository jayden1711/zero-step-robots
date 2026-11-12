The robot has walked backward in every round so far, and I think the thigh sign convention is the cause.

**Evidence that the thigh convention is reversed.**
- The data in rounds 0–4 fit "negative thigh angle = leg swung *forward* relative to the torso". In round 0 the torso was at −0.7 and the thighs reached −0.66, with the robot falling backward. That only adds up if the feet were far ahead.
- The stated fact that negative hip torque with a planted foot pitches the torso backward also only fits this reading.
- Under this reading my thigh rhythm was backwards. During stance (φ ∈ (0, π), knee straight) the thigh target went from 0 to −0.6, which moved the planted leg forward and pushed the body backward.
- That explains the steady backward speed in every round, from −0.4 to −0.8 m/s. It also explains why leaning the torso forward in round 4 didn't help.

**Changes for round 5**
- **Thigh rhythm reversed.** The thigh target is now −0.3 − 0.3·cos φ.
  - In stance the leg sweeps from −0.6 (forward) to 0 (back), pushing the body forward.
  - In swing it returns forward while the knee is flexed.
  - The knee timing is unchanged, so it still flexes in swing and stays straight in stance.
- **Torso balance back to the round-3 gain.** The gain is 2.5 per hip; round 3 had less thigh saturation (21%) than round 4 (86%). The torso damping coefficient stays at about 0.03 per hip.
- **New torso setpoint.** The target is 0.2 − 0.2·vx. A slight forward lean puts the average foot (thigh at −0.3) roughly under the hips. Moving faster lowers the target, so the torso leans back, the feet land further ahead and the robot brakes.
- **Hip bias.** It is −0.36 + 2.5 × 0.2 = 0.14, so the starting torque is small.
- **Unchanged:** the knees, the ankles, and the 0.9 Hz antiphase oscillators.

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
 "bias": {"a0": 0.14, "a1": -0.75, "a2": 0.0, "a3": 0.14, "a4": -0.75, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_speed",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.012, "obs[8]": 0.2},
    "range": 1.6, "tol": 0.02, "to": {"a0": -2.5, "a3": -2.5}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": -0.36, "obs[2]": -1.2, "obs[11]": -0.08},
    "range": 2.5, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 1.433, "cos(R)": 0.443, "obs[3]": -2.5, "obs[12]": -0.1},
    "range": 5.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": -0.36, "obs[5]": -1.2, "obs[14]": -0.08},
    "range": 2.5, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 1.433, "cos(L)": 0.443, "obs[6]": -2.5, "obs[15]": -0.1},
    "range": 5.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```