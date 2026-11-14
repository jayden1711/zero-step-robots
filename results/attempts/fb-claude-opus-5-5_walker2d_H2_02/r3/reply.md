Round 2 got further, surviving 1.6 s, and the hips no longer chattered. But the whole robot fell slowly backward. The torso settled near −0.3 rad while the thighs averaged about −0.15. The leg's tilt from vertical is (thigh − torso), so the feet stayed ahead of the hips and the centre of mass stayed behind the support. Nothing in the controller pushed it forward, so it drifted backward and fell. Both feet were also on the ground about 80% of the time, so there was barely any stepping.

Changes for round 3:

- **Torso target moved forward.** The torso target is now about 0, not −0.2. The thigh centre is −0.3, so on average the feet sit behind the hips. The body then tends to fall forward and has to catch itself by stepping.
- **Speed regulation through lean.** The torso target is now −0.1·(forward speed). Moving fast makes the torso lean back, which puts the feet further forward and brakes. Moving backward makes it lean forward. The balance gain is up from 1 to 2.5 per hip. The angular-velocity damping per hip is unchanged at 0.03, which stays under the chatter limit.
- **Bigger stride and clearance.**
  - Thigh target: −0.3 + 0.3·cos φ, spanning [−0.6, 0], with Kp 1.2.
  - Knee target: −0.3 + 0.6·sin(φ + 0.3), with Kp 2.5. The knee stays pressed straight in stance and flexes to about −0.9 in swing, so the swing foot actually lifts.
- **Ankles unchanged.** A soft hold at 0. Oscillators: 0.9 Hz, antiphase coupling as before.

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
 "bias": {"a0": -0.36, "a1": -0.75, "a2": 0.0, "a3": -0.36, "a4": -0.75, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_speed",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.012, "obs[8]": 0.1},
    "range": 1.5, "tol": 0.02, "to": {"a0": -2.5, "a3": -2.5}},
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