# Round 3: lean the legs forward from the ankles, keep the hips off their limit, keep stance knees straight

## What round 2 shows

- **The balance sign is settled.** Every run is consistent with this: with a foot planted, the torso angle moves together with the thigh joint angle (obs[1] − thigh angle stays roughly constant), and positive thigh torque pitches the torso forward.
- **The hips could not act in the direction balance needed.** In round 2 the thighs stayed between −0.07 and +0.05 rad, which is the 0 limit. The torso tilted back, so the balance term asked for positive thigh torque. That only pushed the hips against their stop and did nothing.
  - The robot then tipped backward as one rigid inverted pendulum, legs in line with the torso and feet ahead of the hip.
  - Because the hips only extend (range ≤ 0), a backward tilt like this cannot be corrected at the hip.
- **The thighs never stepped.** The balance term kept them at the limit, so there were only 2 to 5 touchdowns.
- **Stance knee flexion makes it worse.** With hips that cannot flex, a bent stance knee (−0.3 to −0.5) forces the torso backward, which is the "sitting down" failure.
- **The ankles can only catch a forward fall.** The foot extends forward from the ankle (toe lever about 0.26 m, heel about 0.06 m). So the robot should be kept leaning slightly forward over its feet.

## Changes

- **Foot PD target is now +0.1 rad (toe-up), with gain 2.** With the foot flat, this holds the shanks tilted about 0.1 rad forward. The centre of mass then sits over the toe lever, which the ankle can hold. Because the legs are behind the body, the hips sit near −0.1 rad, away from the limit, so the balance torque has room to act in both directions.
- **Thigh target is −0.2 + 0.2·sin φ.** It moves between −0.4 and 0, with gain 0.8, so stance sweeps the leg backward. Torso balance is −2.5·obs[1] − 0.3·obs[10] per hip. Speed feedback is −0.15·obs[8]: at higher speed the torso leans back, so feet can land further forward and slow the robot.
- **Knees are straight in stance and flex more in swing.** The reflex now adds +1.2 in stance (locked at 0) and −1.2 when cos φ > 0.3, giving about −0.6 rad of flexion for clearance.
- **Start phases are now 1.87 and −1.27.** The right leg starts early in stance and the left starts early in swing. This avoids flexing a knee at t = 0 while both legs carry the weight.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.87},
   {"name": "L", "freq_hz": 0.9, "phase0": -1.27}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.0, "a3": 0.0, "a2": 0.2, "a5": 0.2},
 "units": [
   {"type": "linear", "name": "R_thigh_pd_balance",
    "inputs": {"sin(R)": 0.16, "obs[2]": -0.8, "obs[11]": -0.08, "obs[1]": -2.5, "obs[10]": -0.3, "obs[8]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"cos(R)": 1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a1": -1.2}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -2.0, "obs[13]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh_pd_balance",
    "inputs": {"sin(L)": 0.16, "obs[5]": -0.8, "obs[14]": -0.08, "obs[1]": -2.5, "obs[10]": -0.3, "obs[8]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -2.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"cos(L)": 1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a4": -1.2}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -2.0, "obs[16]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## How I'll read the results

- **It still tips backward with the thighs near 0:** I'll raise the foot toe-up target or add a negative thigh bias.
- **It falls forward quickly:** I'll lower the foot target, strengthen the speed feedback, or raise the frequency.
- **It stands but makes little progress:** I'll raise the thigh amplitude and add a toe-down push-off late in stance.