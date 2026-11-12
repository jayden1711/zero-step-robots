Round 3 survived much longer (4 of 10 episodes reached 8 s) but drifted backward at −0.41 m/s. The trace shows why.

**What went wrong**
- The torso settled at −0.1 to −0.4 rad even though its target was about 0. The centre of mass therefore stayed behind the support.
- The drift happened mostly in double support, with both feet down 82–87% of the time. The body slowly toppled backward between steps rather than being pushed backward by the stride.
- The speed term (−0.1·vx) was far too weak to correct this. At −0.4 m/s it moved the target by only 0.04 rad.
- The gait phasing itself looks right. The right foot lifted exactly during its swing phase, around φ ≈ 3.8–4.4.

**Changes for round 4**
- **Forward lean setpoint and stronger speed regulation.** The torso target is now 0.175 − 0.25·vx:
  - about +0.28 rad when moving backward at 0.4 m/s,
  - +0.175 when standing,
  - +0.05 at 0.5 m/s,
  - leaning back above about 0.7 m/s, which places the feet further ahead and brakes.

  This adds about +0.61 of constant hip torque, which pitches the torso forward. The hip bias becomes −0.36 + 0.6125 = 0.2525.
- **Stiffer torso balance.** The gain is 3.5 per hip instead of 2.5, to shrink the steady backward offset.
- **Torso damping unchanged.** The obs[10] coefficient is 0.008, so damping stays at about 0.028 per hip, under the chatter limit seen in rounds 0 and 1.
- **Everything else unchanged:** thigh and knee rhythm, ankles, 0.9 Hz antiphase oscillators.

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
 "bias": {"a0": 0.2525, "a1": -0.75, "a2": 0.0, "a3": 0.2525, "a4": -0.75, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_speed",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.008, "obs[8]": 0.25},
    "range": 1.6, "tol": 0.02, "to": {"a0": -3.5, "a3": -3.5}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.36, "obs[2]": -1.2, "obs[11]": -0.08},
    "range": 2.5, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 1.433, "cos(R)": 0.443, "obs[3]": -2.5, "obs[12]": -0.1},
    "range": 5.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.36, "obs[5]": -1.2, "obs[14]": -0.08},
    "range": 2.5, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 1.433, "cos(L)": 0.443, "obs[6]": -2.5, "obs[15]": -0.1},
    "range": 5.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```