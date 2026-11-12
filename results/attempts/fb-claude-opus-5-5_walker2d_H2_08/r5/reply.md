# Round 5 (final): keep the stable round-4 gait and add strong forward drive at the ankles

## What round 4 showed

- **The gait is stable.** All 10 episodes survived the full 8 s, with about 20 touchdowns per foot and nearly identical results across seeds. Rhythm, antiphase coupling, knee clearance and torso balance all work.
- **It walks the wrong way, at a steady −0.84 m/s.** The torso settles at about −0.25 rad (leaning back), well behind its commanded target of about +0.07 rad.
- **Why it goes backward.** The thigh can't swing forward of the torso line (q ≤ 0). So when the torso leans back, the swing thigh at its 0 limit lands the foot about 0.25 rad ahead of the hip. Every step lands in front of the centre of mass, and the walker keeps falling backward onto the next step.
- **The hips can't fix this.** Earlier rounds pushed the hip sum both ways and both failed backward:
  - Strongly negative (round 1): the torso pitched back.
  - Strongly positive (round 2): the thighs pinned at 0 and the robot tipped back as one rigid piece.
  - Round 4 sits in between and is the only stable one.

## Change: the ankles

- **What's left to use:** the ankles. In round 4 the foot torque was only about +0.29 at −0.84 m/s.
- **Why it works:** a toe-up ankle torque on a planted foot rotates the shin top-forward, which tips the whole body forward over its feet.
- **The new ankle speed loop:** 0.5·(0.6 − v), built from a +0.3 bias and a −0.5·obs[8] gain on each foot unit.
  - At rest it gives +0.3.
  - At −0.8 m/s it gives +0.7.
  - It falls to zero at +0.6 m/s.
  - So the faster the robot drifts backward, the harder the ankles tip it forward.
- **Foot unit range** raised from 1.5 to 2.5 so the larger input stays linear.

Everything else is copied from round 4 unchanged: oscillators, couplings, torso unit, scissor unit, knees and foot levelling.

**Risk:** this is the one untested change. If the ankle drive is too strong, the robot could fall forward. Any forward progress beats round 4's −6.7 m, so I accept that risk.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 4.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 4.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.1, "a1": -0.375, "a2": 0.3, "a3": -0.1, "a4": -0.375, "a5": 0.3},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": -1.0, "obs[10]": -0.06, "obs[8]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "hip_scissor",
    "inputs": {"obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.25, "obs[14]": 0.25, "cos(R)": 0.4, "cos(L)": -0.4, "sin(R)": -0.4, "sin(L)": 0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": -0.5}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.83, "cos(R)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.83, "cos(L)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[1]": 0.4, "obs[2]": -0.4, "obs[3]": -0.4, "obs[4]": -0.4, "obs[13]": -0.02, "obs[8]": -0.5, "sin(R)": -0.141, "cos(R)": 0.141},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[1]": 0.4, "obs[5]": -0.4, "obs[6]": -0.4, "obs[7]": -0.4, "obs[16]": -0.02, "obs[8]": -0.5, "sin(L)": -0.141, "cos(L)": 0.141},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```