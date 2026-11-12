# Round 3: flip the torso feedback sign and re-derive the joint signs from the data

## Diagnosis

All three designs failed the same way: the torso went negative and the robot moved toward −x. I now think this came from one consistent sign error.

**1. Newton's law fixes the effect of a hip torque on the torso.** The torso angle and the thigh joint rotate about the same axis. A torque +τ at a hip therefore applies −τ to the torso, so a positive hip-torque sum drives obs[1] down.

**2. My balance terms were positive feedback.** Every round used obs[1] gains with the sign the hint gave ("opposes the sign of obs[1]"). With feet planted, the full loop gain dτ_sum/dθ was negative in all three rounds:
- Round 0: 0
- Round 1: −1
- Round 2: −4

That is neutral or unstable every time. It explains why round 2 was the fastest divergence, with the hips saturated at +1 for 66% of steps.

**3. A thigh angle below 0 puts the foot forward, not back.** Round 2 gives the evidence. The thighs sat at their 0 limit, in line with the torso. The whole body then tilted as one piece to θ ≈ −0.6 and moved toward −x. So the "lean back" sense of the torso and the thigh joint is the same rotation, which means q_thigh < 0 is hip flexion (foot forward). The thigh range [−2.62, 0] is a normal flexion range. This also explains the earlier rounds:
- Rounds 0 and 1 commanded negative thigh angles, which put the feet ahead of the body.
- The robot then tipped back over its heels.
- The positive-feedback balance terms amplified that tip.

## Changes

- **Torso unit (sum to both hips).** τ = +1.0·θ + 0.06·θ̇ + 0.1·v − 0.3.
  - This holds a forward lean of about 0.3 − 0.1·v.
  - The forward lean is needed because the thigh cannot extend past the torso line. Without it, the stance foot could never get behind the hip.
  - Gain check: stiffness about 200 N·m/rad on a torso inertia of about 0.2 gives ω·dt ≈ 0.25. The damping is near critical.
- **Scissor unit (difference of the two hips).** The per-leg thigh target is −0.25·cos φ: forward at touchdown (φ = 0), back at lift-off (φ = π).
  - The feedforward is +0.25·sin φ per hip: it pushes the stance leg back and pulls the swing leg forward.
  - Both signs are flipped relative to round 2, to match the corrected convention.
- **Foot units.** The level-foot term now uses the absolute foot angle θ + q_thigh + q_leg + q_foot, so the sign of obs[1] is flipped.
  - The push-off feedforward is flipped and made smaller (+0.15·sin(φ − π/4)), because positive foot rotation is toe-down under the corrected convention.
- **Unchanged.** The knee units, the 1 Hz oscillators, the antiphase coupling, and the start phases (π/2 and 3π/2).

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
 "bias": {"a0": -0.3, "a1": -0.375, "a3": -0.3, "a4": -0.375},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": 1.0, "obs[10]": 0.06, "obs[8]": 0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "hip_scissor",
    "inputs": {"obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.2, "obs[14]": 0.2, "cos(R)": -0.5, "cos(L)": 0.5, "sin(R)": 0.5, "sin(L)": -0.5},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": -0.5}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.83, "cos(R)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.83, "cos(L)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[1]": -0.4, "obs[2]": -0.4, "obs[3]": -0.4, "obs[4]": -0.4, "obs[13]": -0.02, "sin(R)": 0.106, "cos(R)": -0.106},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[1]": -0.4, "obs[5]": -0.4, "obs[6]": -0.4, "obs[7]": -0.4, "obs[16]": -0.02, "sin(L)": 0.106, "cos(L)": -0.106},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## What I'll check next

- **Torso now holds near +0.2 to +0.3 but the robot falls by height:** the problem is in the gait (stride, knees or feet), not balance. I'd tune the scissor amplitude and feedforward.
- **Torso diverges positive (forward):** the sign hypothesis is wrong somewhere. I'd lower the lean bias and re-check.
- **Fast torso oscillation:** lower the obs[10] gain.