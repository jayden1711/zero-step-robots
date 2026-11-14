# Round 4: restore the stabilising balance sign and decouple the hips from the torso

## What round 3 showed

- **The balance sign in rounds 0 to 2 was right, and round 3 broke it.** Round 3 died in 0.06 s, before either foot touched down. The hip bias was −0.55 per hip, and the obs[1] and obs[10] gains were positive.
  - A negative hip torque drove obs[1] negative.
  - That made the hip torque more negative, a runaway loop.
  - The torso centre also moved towards −x, so negative obs[1] is a backward lean.
- **The brief's conventions match all the data.**
  - A positive obs[1] means a forward lean.
  - A negative thigh angle swings the leg backwards.
  - A negative hip torque pitches the torso back.
  - The leg's world angle, with foot-forward positive, is φ = obs[thigh] − obs[1].
  - Upright feedback must have negative gain on obs[1] and obs[10].
- **Why rounds 0 to 2 still drifted backwards.** Each hip tracked a joint-angle target with a large negative constant. In double stance this works like a constant negative torque on the torso. That torque fought a weak balance term, so the torso settled at about −0.45 and the feet ended up well ahead of the hip.

## Design for round 4

1. **Hips track the leg's world angle, not the joint angle.** The hip torque is:
   τ = Kp·(φ* − (q − β)) − Kd·(q̇ − β̇) − Kb·(β − β*) − Kbd·β̇
   with Kp = 1, Kd = 0.1, Kb = 2, Kbd = 0.25.
   - With symmetric leg targets, the tracking terms cancel across the two planted legs, so the torso settles at β* instead of being dragged back.
   - The net gain is −1.0 on obs[1] and −0.15 on obs[10]. The stance leg gives −2, so the loop is clearly stabilising.
2. **Leg target and lean target.**
   - The leg follows φ* = −0.08 + 0.16·cos φ, so the stance phase runs from +0.08 (foot ahead) to −0.24 (push-off). On average the feet are slightly behind the hip, which tips the robot forward.
   - The torso target is a small backward lean, β* = −0.07 − 0.1·v. Leaning back is the only way a thigh limited to ≤ 0 can put the foot ahead.
   - With these targets the thighs stay in about [−0.36, −0.04], clear of the 0 limit.
   - Speed control: going too fast leans the torso further back, and going too slow or backwards leans it forward.
   - The bias is Kp·(−0.08) + Kb·(−0.07) = −0.22.
3. **Knee target: −0.2 + 0.55·sin(φ + 0.3), Kp = 1.5.**
   - In stance the knee is held straight against its limit.
   - It flexes to about −0.75 early in the swing and is almost straight at foot strike.
4. **Frequency 0.9 Hz, symmetric start.** The oscillators start at π/2 and 3π/2, so both hips get the same opening torque. The ankles keep their soft PD.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.22, "a1": -0.3, "a3": -0.22, "a4": -0.3},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.16, "obs[2]": -1.0, "obs[1]": -1.0, "obs[11]": -0.1, "obs[10]": -0.15, "obs[8]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.79, "cos(R)": 0.24, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.16, "obs[5]": -1.0, "obs[1]": -1.0, "obs[14]": -0.1, "obs[10]": -0.15, "obs[8]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.79, "cos(L)": 0.24, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

**What to change in round 5:**
- If the torso still settles well below −0.2 and the robot drifts backwards, I'll make the leg centre c more negative and β* less negative.
- If it now falls forward, I'll do the opposite.