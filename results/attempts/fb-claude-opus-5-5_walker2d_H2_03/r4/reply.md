Round 3 fell backward the same way rounds 0 and 2 did, so the cause is structural rather than a matter of gains.

**Diagnosis**
- **The hip has no room to correct the torso.** In round 3 both thighs sat at their 0 stop (max +0.02 and +0.04) while the torso drifted back. A hip that is pressed against its limit can't push the torso forward. The robot then tips backward over its feet as one rigid body.
- **The start was asymmetric.** With phases 0 and π, the left thigh's target was −0.45 at t = 0 while its foot was planted. That negative torque pitched the torso backward (−0.12 by 0.1 s), and the right thigh was pinned at its +0.05 target.
- **Geometry.** Thigh world tilt = obs[1] − q_thigh, with q_thigh ≤ 0. So with an upright torso, the feet can only be under or behind the hip. The gait must therefore keep the torso nearly upright, keep the thighs inside their range, and push the stance leg back from under the hip.

**Changes**
- **Start phases at π/2 and 3π/2.** Both thigh targets equal the centre (−0.2) at t = 0, so the start transient is about −0.04 instead of ±0.45. The right leg starts in mid-stance with a straight knee, and the left leg starts in mid-swing.
- **Thigh target range kept off the stop.** The target is −0.2 + 0.15·cos φ, so it ranges from −0.35 to −0.05. With an upright torso, the stance leg sweeps from under the hip to about 0.35 rad behind it.
- **Stronger torso feedback with the same sign as rounds 0, 2 and 3.**
  - The posture term is −2.0·obs[1] − 0.06·obs[10] + 0.16.
  - Adding the thigh velocity term gives about 0.11 damping per hip. That is roughly critical damping and stays stable at the 8 ms step.
  - The target lean is +0.08 rad.
- **Speed feedback.** A −0.1·obs[8] term leans the torso target back as speed rises, so the swing foot lands further forward.
- **Knee.** The target is −0.25 + 0.55·sin φ. It stays straight in stance and flexes to about −0.8 in swing.
- **Unchanged:** the feet, the oscillators and the coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.04, "a1": -0.375, "a2": 0.0, "a3": -0.04, "a4": -0.375, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"obs[2]": -1.0, "obs[11]": -0.05, "cos(R)": 0.15, "obs[1]": -2.0, "obs[10]": -0.06, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.03},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"obs[5]": -1.0, "obs[14]": -0.05, "cos(L)": 0.15, "obs[1]": -2.0, "obs[10]": -0.06, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.825},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.03},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```