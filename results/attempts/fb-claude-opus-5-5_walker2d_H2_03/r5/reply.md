# Round 5 (final): fix the whole-body backward tip

**Diagnosis**

In rounds 0, 3 and 4 the torso angle was not really the problem; it only showed that the whole body was rocking backward over the heels.

- **Round 4 numbers.** For the first 0.7 s, both feet were on the ground. The thighs sat at their 0 stop, the torso angle was about −0.25 and the height was 1.20 m (1.25·cos 0.25 ≈ 1.21).
  - From that data, the leg's world angle is q_thigh − obs[1] ≈ +0.25. So the feet were ahead of the hip, and the whole robot was tilted back as one rigid body.
  - The foot angles never went below about −0.1. So the feet were not flat: the toes had lifted and the robot was pivoting on its heels.
- **Why this starts so easily.**
  - Each foot extends 0.2 m forward of the ankle, so the heel is at the ankle.
  - The foot target of 0 keeps the shins vertical. That puts the centre of mass right over the heel edge, which is only marginally stable.
  - The start-up knee flexion in rounds 0 and 4 (a loaded knee bending) pushes the hip back and drags the torso against the hip stop.
  - The legs weigh about 20 kg and the torso about 3.7 kg. So the leg and ankle placement decide the balance, not the torso lean.

**Changes**

- **Ankle (the main fix).**
  - The foot target is now +0.1 + 0.1·cos φ. This tilts the shin forward and puts the centre of mass over the middle of the foot instead of the heel. The target is +0.2 just after touchdown (so the body rolls forward) and 0 at the end of stance (push-off).
  - Ankle stiffness is doubled to Kp = 2.0. Two feet then give about 400 Nm/rad, against about 150 Nm/rad of gravity tipping.
  - Speed feedback −0.15·(vx − 0.5): if the body moves backward, the ankles push the shins forward; if it goes faster than about 0.5 m/s, they brake.
  - Ankle damping is 0.04. That is still numerically stable for the foot's small inertia.
- **Knee.** The target is 0 + 0.8·sin φ.
  - At both start phases (0 and π) the target is 0, so neither knee bends at t = 0.
  - In stance the target is positive, so the knee is held straight against its stop.
  - In mid-swing it flexes to −0.8, which lifts the foot about 0.24 m.
- **Thigh.**
  - The target is −0.2 + 0.15·cos φ, so it ranges from −0.05 to −0.35 and stays mostly off the stop.
  - Torso feedback is −1.5·obs[1] − 0.06·obs[10], which is milder than round 4 (round 4 saturated 27% of the time).
  - A small −0.1·(vx − 0.5) term leans the torso back when the robot goes too fast.
  - Damping stays in the range that worked in round 4.
- **Unchanged:** the 1 Hz oscillators with antiphase coupling, and the start phases (R = 0, L = π).

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
 "bias": {"a0": -0.15, "a1": 0.0, "a2": 0.275, "a3": -0.15, "a4": 0.0, "a5": 0.275},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.05, "cos(R)": 0.15, "obs[1]": -1.5, "obs[10]": -0.06, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 1.2},
    "range": 3.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -2.0, "obs[13]": -0.04, "cos(R)": 0.2, "obs[8]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.05, "cos(L)": 0.15, "obs[1]": -1.5, "obs[10]": -0.06, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 1.2},
    "range": 3.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -2.0, "obs[16]": -0.04, "cos(L)": 0.2, "obs[8]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```