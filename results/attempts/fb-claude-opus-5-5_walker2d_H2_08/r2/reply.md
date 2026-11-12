# Round 2: decoupled hip control

**Diagnosis.** Round 1 fell backward because of the targets I set, not because of a sign error. Two checks support this:
- **The sign convention is right.** The large negative hip bias drove the torso angle negative, and the robot then moved toward −x. Both match the spec's conventions. Under the opposite convention, the torso would have pitched positive.
- **The torso settled where I told it to.** With both feet planted, the light torso settles where the two hip torques sum to zero. For round 1's gains that is about θ = −(1.44 + ψ_R + ψ_L)/5, where ψ is each planted leg's forward angle from vertical. With the legs near vertical that gives about −0.3 rad, which is what the results showed (−0.32 to −0.39). That backward lean put both feet about 0.35 rad ahead of the hips. The centre of mass, which is mostly the legs, sat behind the feet, so the robot tipped backward about its heels.

**New structure.** The torso is light, so it responds to the sum of the two hip torques. The thigh-difference q_R − q_L does not depend on the torso angle. So I split hip control into two units:

1. **Torso unit (sum mode).** It sends the same command to both hips: 0.2 − 2·θ − 0.08·θ̇ − 0.3·v.
   - At equilibrium this holds θ ≈ 0.1 − 0.15·v. That is a slight forward lean at low speed and upright at about 0.7 m/s.
   - If the torso pitches forward, the negative stance-hip torque rotates the stance leg back and moves the hip forward under the torso. If the robot goes too fast, the torso leans back, which brakes the hip and lets the swing foot land further forward.
   - Gain checks: the stiffness gives ω·dt ≈ 0.36 and the damping gives about 0.64 per step. Both are well inside the stability limits.
2. **Scissor unit (difference mode).** It sends +½ of its output to a0 and −½ to a3.
   - It does PD tracking of q_R − q_L toward 0.2·(cos φ_R − cos φ_L). Each thigh's share is effectively ±0.2·cos φ.
   - It adds a feedforward of −0.3·sin φ per leg: the swing leg is pulled forward and the stance leg pushed back.
   - The mean thigh angle is no longer commanded, so the hips can no longer impose a torso lean.

**Start phases.** R starts at π/2 (mid-stance) and L at 3π/2 (mid-swing). This matches the initial pose, with the legs together, so the scissor target is 0 at t = 0.

**Unchanged.** The knee units, the foot units, and the oscillators at 1 Hz with antiphase coupling. The design uses 6 of the 16 hidden units.

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
 "bias": {"a0": 0.2, "a1": -0.375, "a3": 0.2, "a4": -0.375},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": -2.0, "obs[10]": -0.08, "obs[8]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "hip_scissor",
    "inputs": {"obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.15, "obs[14]": 0.15, "cos(R)": 0.4, "cos(L)": -0.4, "sin(R)": -0.3, "sin(L)": 0.3},
    "range": 3.5, "tol": 0.05, "to": {"a0": 0.5, "a3": -0.5}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.83, "cos(R)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.83, "cos(L)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[1]": 0.4, "obs[2]": -0.4, "obs[3]": -0.4, "obs[4]": -0.4, "obs[13]": -0.02, "sin(R)": -0.21, "cos(R)": 0.21},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[1]": 0.4, "obs[5]": -0.4, "obs[6]": -0.4, "obs[7]": -0.4, "obs[16]": -0.02, "sin(L)": -0.21, "cos(L)": 0.21},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

**What I'll check next:**
- **Falls forward by torso angle:** lower the 0.2 hip bias, or raise the speed gain.
- **Falls backward:** raise the bias, which gives more forward lean.
- **Shuffling with little progress:** raise the scissor amplitude or the feedforward.
- **Fast torso oscillation:** lower the obs[1] and obs[10] gains.