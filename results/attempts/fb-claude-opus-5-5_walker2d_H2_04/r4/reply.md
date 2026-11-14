# Round 4: lean the torso slightly back and keep the stance knee locked

Rounds 0, 1 and 3 all fell slowly backward, with the right thigh pinned near its 0 limit. I think I had the geometry wrong, and here is the corrected reasoning.

**What the data says**
- **The hip can only swing the leg backward.** The thigh range is [−2.62, 0], and negative swings the leg backward. So at q = 0 the leg is exactly in line with the torso, and it can never be ahead of the torso line.
  - If the torso leans forward, the feet must sit behind the hip. The robot then cannot stand or catch itself.
  - For the feet to sit under the hip, or for a leg to reach forward, the torso must lean back. Leg tilt = torso angle − q.
- **My forward-lean setpoints did nothing useful.** In rounds 1 and 3 the balance unit asked for a forward lean, which is positive thigh torque. Both thighs sat at their limit (q ≈ 0 to 0.05), so that torque pushed into the joint stops and had no effect.
- **Knee flex in stance throws the torso back.** Flexing a knee with the foot planted tips the thigh top backward. With the hip at its limit, the torso goes back with it.
  - All earlier designs bent the stance knees (bias −0.6 to −1.5).
  - So the whole body tipped backward like a stick, and x went negative.

**Revisions**
- **Torso setpoint is about −0.2 rad (leaning back).** It is set by speed: r* = −0.19 − 0.1·obs[8], so it leans back more when moving fast and less when slow.
  - Balance term: −3·(obs[1] − r*) − 0.6·obs[10], on both thighs.
  - The sign follows the hint. The setpoint is now reachable, so the thighs keep room to push both ways.
- **Thigh rhythm:** target −0.25 + 0.2·cos φ, so q runs from −0.05 at touchdown (φ = 0) to −0.45 at liftoff.
  - The leg tilt in the world then runs from about −0.2 (foot ahead) to +0.2 (foot behind).
  - The PD term is Kp = 1.5, Kd = 0.15.
  - At standing equilibrium (obs[1] = −0.19, q = −0.25) the total thigh torque is 0.
- **Knee:**
  - A reflex gives +0.9 torque, holding the knee locked straight, through stance and late swing.
  - It gives −0.9, flexing the knee, from liftoff until about 0.12 s before touchdown.
  - A weak PD toward straight sets the swing flexion to about −0.6.
- **Start phases are π/2 and 3π/2,** so both thigh targets start equal. This avoids a lopsided start; the left leg starts in swing.

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
 "bias": {"a0": -0.945, "a3": -0.945},
 "units": [
   {"type": "linear", "name": "torso_balance_speed",
    "inputs": {"obs[1]": -3.0, "obs[10]": -0.6, "obs[8]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.3, "obs[2]": -1.5, "obs[11]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.3, "obs[5]": -1.5, "obs[14]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "reflex", "name": "R_knee_swing_flex",
    "inputs": {"sin(R)": -0.921, "cos(R)": -0.389}, "threshold": 0.3,
    "sharpness": 5.0, "to": {"a1": -0.9}},
   {"type": "reflex", "name": "L_knee_swing_flex",
    "inputs": {"sin(L)": -0.921, "cos(L)": -0.389}, "threshold": 0.3,
    "sharpness": 5.0, "to": {"a4": -0.9}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```