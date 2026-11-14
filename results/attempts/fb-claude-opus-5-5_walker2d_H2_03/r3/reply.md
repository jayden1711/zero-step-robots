Round 2 fell backward again, and I think the main cause was not posture but a numerical instability in the damping.

**Diagnosis**
- **The damping is too strong for the time step.** Each hip received about 0.5 × 100 Nm per rad/s of damping on the torso: 0.4 from obs[10] plus 0.1 from the thigh velocity. That acts on a torso that weighs about 3.7 kg, with inertia about the hip of about 0.2 kg·m². With 8 ms steps this gives c·dt/I ≈ 3. The damping term overshoots every step and the hip torque flips between +1 and −1.
- **This matches the data.**
  - The thigh actions were saturated 91% of the time.
  - The thigh units were saturated 46% of the time.
  - The torso still tipped back slowly, over about 0.8 s. That is the speed of gravity acting with near-zero average hip torque. A steady ±100 Nm hip torque would have moved it within milliseconds.
- **The backward bias has a second cause: the heel.** Each foot extends forward from the ankle, so the heel is at the ankle. Leaning the torso back puts the centre of mass behind the heel. I'm moving the torso target back to upright (0). The gait will then fall forward over a stance leg that sweeps from under the hip to behind it, which also gives a positive d.

**Changes**
- **Damping lowered.** Thigh Kd is 0.05 and the obs[10] gain is 0.05, about 0.1 per hip in total. The two hips together give roughly critical damping and stay well inside the stable range for an 8 ms step. The knee and foot damping stay modest; the foot's goes down to 0.03.
- **Thigh.** The target is −0.2 + 0.25·cos φ with Kp = 1.0, plus −1.0·obs[1] (target lean 0). The stance leg sweeps from under the hip to about 0.45 rad behind it.
- **Knee.** The target is −0.15 + 0.55·sin φ with Kp = 1.5.
  - In stance it is clipped straight.
  - In swing it flexes to about −0.7.
- **Unchanged:** the oscillators and the coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.2, "a1": -0.225, "a2": 0.0, "a3": -0.2, "a4": -0.225, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.05, "cos(R)": 0.25, "obs[1]": -1.0, "obs[10]": -0.05},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.05, "cos(L)": 0.25, "obs[1]": -1.0, "obs[10]": -0.05},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```