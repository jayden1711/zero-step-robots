# Round 4: keep the hips off their limit, hold the torso with the hips, push forward with the ankles

## What rounds 1 to 3 show

- **The relation that matters.** With a foot planted, obs[1] − (thigh angle) stays constant. So the world angle of a leg, foot-forward positive, is (thigh angle) − obs[1].
  - The hips can only extend (thigh angle ≤ 0).
  - So a foot can land ahead of the hip only when the torso leans back.
  - If the stance thigh sweeps back while the body does not move forward over the foot, the torso is pitched backward instead.
- **That is the backward drift seen in every round:**
  - The rhythm pulls the stance thigh back.
  - The torso tilts back.
  - The balance term asks for positive thigh torque, but the thigh is at its 0 limit, so the torque does nothing.
- **Lifting a leg backward moves the centre of mass backward.** The legs are about 85% of the mass. The robot then tips back.
- **Round 3's ankles worked against forward motion.** They used a stiff hold near 0 rad. As the shin tilts forward during stance, that hold pushes the body back.
- **The knees bent in stance**, to −0.4 rad on both legs (sitting).

## Changes

1. **Thigh rhythm is offset negative:** target −0.28 + 0.2·sin φ, between −0.48 and −0.08.
   - The stance thigh now stays off its 0 limit.
   - The PD gain is lowered to 1.0 so the balance term dominates.
2. **Torso balance is stronger, with speed fed into the lean target:**
   - Torso target = 0.08 − 0.4·v, with gain 3 and damping 0.3.
   - When the robot is fast, the torso leans back. A thigh at about −0.08 then lands the foot ahead of the hip, which brakes.
   - When the robot is slow, the torso is upright and the robot falls forward onto the next step.
3. **Ankles drive forward progress:**
   - Weak PD towards +0.1 rad, plus a forward torque of 0.2 − 0.3·v.
   - This tips the body forward over the foot at low speed and fades out at higher speed.
   - In swing, the positive torque also lifts the toe for ground clearance.
4. **Knee flexion only in early and mid swing:**
   - The window is cos(φ + 0.3) > 0.54, which is φ in (−1.3, 0.7).
   - Inside the window the knee flexes to about −0.8 rad.
   - Outside it the knee is pushed straight against its limit, so it stays straight through all of stance and is extended before touchdown.
5. **Timing:** 1.0 Hz. The start phases put the right leg early in stance and the left leg at the start of its forward swing.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 2.2},
   {"name": "L", "freq_hz": 1.0, "phase0": -0.94}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.04, "a3": -0.04, "a2": 0.32, "a5": 0.32},
 "units": [
   {"type": "linear", "name": "R_thigh_track_balance_speed",
    "inputs": {"sin(R)": 0.2, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -3.0, "obs[10]": -0.3, "obs[8]": -1.2},
    "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.6, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 0.955, "sin(R)": -0.296}, "threshold": 0.54, "sharpness": 6.0,
    "to": {"a1": -1.3}},
   {"type": "linear", "name": "R_ankle_pd_speed",
    "inputs": {"obs[4]": -1.2, "obs[13]": -0.1, "obs[8]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_track_balance_speed",
    "inputs": {"sin(L)": 0.2, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -3.0, "obs[10]": -0.3, "obs[8]": -1.2},
    "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.6, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 0.955, "sin(L)": -0.296}, "threshold": 0.54, "sharpness": 6.0,
    "to": {"a4": -1.3}},
   {"type": "linear", "name": "L_ankle_pd_speed",
    "inputs": {"obs[7]": -1.2, "obs[16]": -0.1, "obs[8]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## How I'll read the results

- **It still drifts backward with the torso tilted back:** I'll raise the ankle forward bias and lower the thigh offset.
- **It falls forward (torso angle above +1, or fast forward speed then a fall):** I'll raise the speed gain on obs[8] (more lean-back when fast) and lower the ankle bias.
- **It sits down (knees bent in stance):** I'll narrow the flexion window.