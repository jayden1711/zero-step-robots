# Round 5: fix the feedback loop that has been oscillating, and recentre the support

**What I think the data shows**

- **The thigh feedback has been oscillating at the step rate.** In every round the thighs sat at |action| ≥ 0.99 for 54–94% of steps. That points to a feedback loop that is unstable, not just weak.
  - The torso is light: about 3.7 kg, with an inertia about the hip of about 0.2 kg·m². The thighs act on it with up to 100 N·m per unit of action.
  - In round 4 the velocity gains on the torso added up to about 1.5 action units, which is 150 N·m·s. Over one control step, 150 × 0.008 / 0.2 ≈ 6, far above the stability limit of about 2. The feedback overshot every step and the thighs flipped between the two action limits, which is what the table shows.
- **The robot starts at the back edge of its support.** The foot sticks out forward of the ankle, from about −0.06 m to +0.26 m. With the legs vertical, the centre of mass sits above that back edge.
  - Every design also pitched the torso back at the start, through bias or knee flex. So each one tipped over backward, and x went negative.
  - The legs carry about 85% of the mass, so the torso's lean barely moves the centre of mass. What matters is the leg tilt.
- **Geometry (unchanged from round 4):** leg tilt = obs[1] − q, with q ≤ 0. A slight backward torso lean of about −0.1 rad still lets the swing foot land just ahead of the hip.

**Revisions**

- **Torso loop sized for the 0.008 s step.** I worked out these numbers by hand.
  - Total stiffness on the torso is about 3.2 units, which is 320 N·m/rad.
  - Total torso damping is 0.1 unit, which is 10 N·m·s. That gives a per-step factor of 10 × 0.008 / 0.2 ≈ 0.4 and a damping ratio of about 0.6.
- **Thigh damping no longer acts on the torso.** The thigh velocity term uses −0.15·(q̇ − obs[10]), which depends only on how fast the leg tilts in the world.
  - This damps the heavy swing leg without destabilising the torso.
- **Thigh rhythm:** the PD gain is Kp = 0.8, and the target is −0.25 + 0.2·cos φ.
  - At touchdown (φ = 0) the target is q = −0.05, with the foot slightly ahead.
  - At liftoff (φ = π) it is −0.45, with the leg behind.
  - The bias is −0.24, so the torso settles at about −0.1 rad and the stance legs tilt forward. That puts the centre of mass over the middle of the foot.
- **Knee:**
  - The target is −0.2 + 0.45·sin(φ + 0.57). The knee is locked through stance and touchdown, and flexes to about −0.65 in early swing.
  - The PD term is Kp = 1.5 and Kd = 0.15.
- **Foot:** a soft PD with Kp = 0.5 and Kd = 0.02, so the foot settles flat on the ground and its control loop stays stable.
- **Oscillators:** 0.75 Hz, close to the leg's natural swing frequency, with antiphase coupling as before.
- **Failure mode:** if this design still falls, the forward-tilted legs should make it fall forward, which still counts as positive d.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.75, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.75, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.24, "a1": -0.3, "a3": -0.24, "a4": -0.3},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": -0.8, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.02, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "R_thigh_pd",
    "inputs": {"cos(R)": 0.16, "obs[2]": -0.8, "obs[11]": -0.15, "obs[10]": 0.15},
    "range": 2.0, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd",
    "inputs": {"cos(L)": 0.16, "obs[5]": -0.8, "obs[14]": -0.15, "obs[10]": 0.15},
    "range": 2.0, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee_pd",
    "inputs": {"sin(R)": 0.568, "cos(R)": 0.364, "obs[3]": -1.5, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd",
    "inputs": {"sin(L)": 0.568, "cos(L)": 0.364, "obs[6]": -1.5, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```