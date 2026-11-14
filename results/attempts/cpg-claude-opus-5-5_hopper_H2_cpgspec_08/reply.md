This is a hand-reasoned design. I couldn't simulate it, so the gains are physically motivated estimates, not tuned values.

**Gait concept**
- **Posture.** The robot crouches over its long, heavy foot plate:
  - knee about −0.22 rad;
  - foot joint about +0.34 rad, which keeps the plate flat while the shank tilts back;
  - thigh slightly back of vertical.
  
  This puts the centre of mass about 0.15 m ahead of the ankle, inside the support (heel −0.13 m, toe +0.26 m). The rigid stance is then passively stable.
- **Rhythm.** One 2 Hz oscillator drives the hops:
  - **Ankle:** feed-forward toe-down torque, which lifts the body about the toe. This is the main vertical actuator, because the near-straight knee has little leverage on leg length.
  - **Knee:** extension torque in phase with the ankle push. With the shank held by the ankle, knee extension swings the thigh back and drives the hip forward and up.
  - **Start phase:** π, so the first half-cycle unloads and crouches rather than kicking from the straight start pose.
- **Joint damping.** The knee and ankle use PD around the crouched posture. Damping is set to roughly ζ≈0.5, because the armature (1 kg·m²) dominates the joint inertia. This keeps the 2 Hz drive from resonating.
- **Torso balance.** The thigh servoes the torso: a0 = −3·obs[1] − 0.24·obs[7]. This opposes the torso angle and its rate, as the given sign conventions require. Stiffness is about 600 Nm/rad, with near-critical damping at the 8 ms step.
- **Speed regulation through lean.** A saturating unit on obs[5] shifts the torso's target lean by up to about ±0.08 rad around a desired speed of 0.7 m/s:
  - Too slow: lean forward. In flight this swings the leg back, so it lands behind the centre of mass and accelerates.
  - Too fast: lean back. The foot lands ahead and brakes, similar to Raibert foot placement.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 3.1416}],
 "couplings": [],
 "bias": {"a1": -0.33, "a2": 0.41},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.08},
    "range": 1.2, "tol": 0.05, "to": {"a0": -3.0}},
   {"type": "reflex", "name": "speed_lean", "inputs": {"obs[5]": 1.0}, "threshold": 0.7,
    "sharpness": 1.5, "to": {"a0": -0.25}},
   {"type": "linear", "name": "knee_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.06},
    "range": 2.0, "tol": 0.05, "to": {"a1": -1.5}},
   {"type": "linear", "name": "ankle_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.06},
    "range": 2.0, "tol": 0.05, "to": {"a2": -1.2}},
   {"type": "linear", "name": "knee_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.1, "tol": 0.02, "to": {"a1": 0.25}},
   {"type": "linear", "name": "ankle_rhythm", "inputs": {"sin(hop)": 1.0, "cos(hop)": -0.4},
    "range": 1.2, "tol": 0.02, "to": {"a2": -0.25}}
 ]}
```