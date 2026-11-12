# Round 3: fix balance before speed

Round 2 also fell backward, and I believe I misread why. Here is what I now think went wrong, then what changes.

**What went wrong:**
- **The damping gains were far too high for the 0.008 s control step.**
  - With gear 200 and a torso inertia about the hip of roughly 0.2 kg·m², a D gain of 0.8 on obs[7] gives Kd·dt/I ≈ 6. A sampled-data loop is unstable above about 2.
  - That fits the 16–23% of steps with the thigh at ±1: the hip was chattering, not balancing.
  - The foot D (0.1) was also near that limit in flight.
- **My round-2 hip bias pitched the torso backward.** A net a0 of −0.25 does exactly what the facts say a negative thigh torque does.
- **The hip cannot fix a whole-body backward tip.** When the leg is upright, the thigh is pinned at its 0 stop. Pitching the torso forward would need a thigh angle above 0.
  - The fix is ankle balance on the leg's absolute angle, φ = obs[1] − obs[2] − obs[3].
  - The ankle keeps the hip slightly ahead of the foot. That keeps the thigh negative, so the hip has room to act both ways.
- **The foot push had the wrong sign.** A positive foot torque lifts the toes and rocks the robot onto its heel. Push-off needs a negative foot torque (toes down).
  - The heel is only 0.13 m behind the ankle, so even about 0.1 of foot action can roll the foot.
  - Ankle torques must therefore stay small.

**Changes for round 3:**
- **Hip:**
  - Torso PD is now P 5 and D 0.15, which gives Kd·dt/I ≈ 1.3.
  - A light thigh spring pulls toward −0.1.
  - The net a0 bias is small and positive.
- **Ankle:**
  - A gentle PD on φ, targeting 0.08 rad of forward leg lean. It is bounded because the unit saturates.
  - A foot-level term keeps the foot flat in flight. It does nothing on the ground.
- **Knee:** a spring targets −0.15, so both halves of the thrust act.
- **Rhythm:**
  - One 2.5 Hz thrust reflex: knee +0.4 to extend, foot −0.12 to push the toes down, and hip −0.1 to drive the leg back while the leg pushes.
  - The cycle starts in the compression half.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 3.14}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": -0.225, "a2": 0.08},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.15, "obs[5]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_posture", "inputs": {"obs[3]": -1.5, "obs[9]": -0.08},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": -0.1, "obs[8]": 0.1, "obs[9]": 0.1},
    "range": 0.4, "tol": 0.1, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_level", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "thrust", "inputs": {"sin(hop)": 1.0}, "threshold": 0.0,
    "sharpness": 2.0, "to": {"a0": -0.1, "a1": 0.4, "a2": -0.12}}
 ]}
```