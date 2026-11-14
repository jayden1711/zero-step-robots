# Round 2: keep the hips off their joint limit

## What round 1 showed

- **The balance sign was right.** In both rounds the torso leaned to negative angles and the robot moved backwards. The final fall in round 1 was backwards, with x dropping faster and faster. So a negative obs[1] means a backward lean, as the brief says. A negative hip torque also pitched the torso back.
- **The hips were pinned at their limit.** In round 1 both thighs stayed between about −0.16 and +0.05. That is at the 0 limit (the leg in line with the torso), with 31% of hip actions saturated. The balance term and the speed term pushed the thighs up into that limit. At the limit, hip torque cannot rotate the torso. The robot then became a rigid stick and tipped backwards.
- **The stick has its feet in front.** The leg's angle from vertical (forward positive) is about thigh angle − obs[1]. The thighs can only move backwards from the torso line. So the only way to put a foot ahead of the hip is a slight backward torso lean, with the thigh kept below 0. Round 0 settled at a torso angle of −0.45 with the feet mostly ahead, which explains its backward stepping. The fix is a small backward lean with the thighs well clear of 0.

## Design for round 2

1. **Hip target in joint space:** −0.35 + 0.25·cos φ, a range of −0.6 to −0.1.
   - The thigh never asks to reach 0, so the stance hip always has room to correct the torso.
   - With the torso at about −0.25, the leg angle from vertical runs from +0.15 at foot strike to −0.35 at push-off.
   - On average the feet are slightly behind the hip, so the robot tends to fall forward.
   - Kp = 1.0 and Kd = 0.1.
2. **Torso balance:** −1.0·(obs[1] + 0.25) − 0.1·obs[10].
   - The speed term is −0.15·(obs[8] − 0.6). It leans the torso further back when the robot goes too fast and forward when it goes too slow or backwards.
   - The constant part goes into the bias: a0 = a3 = −0.51.
   - With the stance foot planted, a backward torso tilt also lowers the thigh angle, so the joint PD term and the balance term both push the same way.
3. **Knee target:** −0.25 + 0.55·sin(φ + 0.4).
   - Stance runs from φ = 0 (foot strike, thigh most forward) to π. The knee is straight there, held by the 0 limit.
   - The knee starts to flex just before push-off. It is most flexed (−0.8) in mid-swing and almost straight at the next strike.
4. **Starting phases are symmetric** (π/2 and 3π/2). Both thigh targets start equal, so the opening transient pitches the torso less. The right leg starts at mid-stance and the left at mid-swing with its knee flexed.
5. **Frequency is 0.8 Hz.** That should give roughly 0.6 to 0.8 m/s.

**What to test.** If the torso now falls forward, the next change is a smaller lean offset or a less negative hip centre. If it still drifts backwards past −0.4, the next change is a higher Kb.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.51, "a1": -0.375, "a3": -0.51, "a4": -0.375},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.25, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -1.0, "obs[10]": -0.1, "obs[8]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.76, "cos(R)": 0.32, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.25, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -1.0, "obs[10]": -0.1, "obs[8]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.76, "cos(L)": 0.32, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```