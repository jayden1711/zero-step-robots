# Round 2: stronger torso control, a speed term, and less thigh saturation

## Reading the round-1 results

- **The balance sign is now right.** Round 0 settled it: negative thigh torque pitched the torso backward almost at once, so the feedback must oppose obs[1] and obs[10], as in round 1.
- **The torso still drifted backward**, to between -0.5 and -0.74 rad, and the robot moved backward at about -0.66 m/s. It then "sat down" (height too low, knees near -0.5).
- **The balance terms lost out.** The thigh actions were saturated about 75% of the time, and the units were past their declared range 20 to 24% of the time. So the rhythm and the joint-angle terms were swamping the balance terms.
- **Why the torso drifts back:**
  - Each stance stroke (thigh moving backward) and each swing stroke (swing-leg reaction) pushes the torso backward.
  - My balance gain was too weak to undo that.
  - Nothing reacted to the robot moving backward.

## Changes for round 2

- **Balance is the priority.** The torso gains rise to -3.0·obs[1] - 0.4·obs[10] per thigh, about 6 and 0.8 in total.
- **Smaller thigh rhythm and joint gains.** The thigh target is now -0.2 + 0.2·sin φ, with gain 1.5 and damping 0.15. The range rises to 5 so the unit stays linear.
- **Speed feedback on both thighs: -0.3·obs[8].** When the robot slides backward (v < 0), this adds positive thigh torque, which pitches the torso forward and stops the backward run. When the robot goes fast, it leans the torso back. Together with the -0.2 joint offset, this gives a net thigh bias of about 0.
- **Firmer knees:**
  - The stance lock is stronger: gain 2, plus about +0.8 from the reflex.
  - The swing flexion starts a little earlier (cos φ > 0.2) and is a little stronger.
- **Feet:** stiffer hold at 0 rad.
- **Units used:** still 8 of 16.

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
 "bias": {"a0": 0.0, "a3": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.3, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -3.0, "obs[10]": -0.4, "obs[8]": -0.3},
    "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.2, "sharpness": 5.0,
    "to": {"a1": -0.9}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.5, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.3, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -3.0, "obs[10]": -0.4, "obs[8]": -0.3},
    "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.2, "sharpness": 5.0,
    "to": {"a4": -0.9}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.5, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## How I'll read the results

- **The torso still drifts back steadily:** I'll add a positive thigh bias (a forward-lean target) or raise the balance gain.
- **The torso oscillates or falls forward:** I'll lower the balance gain or the speed gain.
- **It is stable but d ≈ 0:** I'll raise the thigh amplitude and the speed set-point.