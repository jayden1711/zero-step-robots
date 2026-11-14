This controller is a squat-and-push hopping rhythm sitting on top of three PD stabilisers. I designed it on paper and could not test it, so whether it passes depends on how the open-loop 2 Hz rhythm meshes with the real contact timing.

**How it works**

- **Torso balance (thigh, a0):** a0 = −3·θ − 0.25·θ̇ − 0.15·v + 0.18.
  - Opposing obs[1] and obs[7] keeps the torso upright.
  - The −0.15·v term is the speed regulator: the upright target is about +0.06 rad at rest, and the torso leans back as speed passes about 0.8 m/s.
  - In flight, hip torque mostly rotates the light torso, not the heavy leg (the foot alone is about 5 kg). So I use the hip only for torso attitude, with no rhythmic thigh swing.
- **Knee (a1):** a PD holding the knee at −0.15 rad, plus a 0.5·sin(phase) torque. Half of each 0.5 s cycle crouches and the other half pushes.
  - If the robot is in the air, the crouch half lifts the foot.
  - If it never leaves the ground, it just bobs in place and does not collapse, so a timing mismatch should not be fatal.
- **Ankle (a2):** a PD on the foot angle with target 0.2 rad, minus 0.1·v.
  - With the foot flat, the foot angle equals the shin's forward tilt, so this PD is the whole-body balance (ankle strategy). It holds the body leaning slightly forward, which sends each push forward.
  - A reflex unit adds a −0.6 toe push-off pulse. It is centred about 0.5 rad after the knee's peak push, near the end of extension.
  - A bias cancels the reflex's resting offset, so the pulse is zero outside its window.
- **Consistency:** the thigh joint cannot go above 0, which forces the torso to lean no further forward than the thigh. I chose the targets (knee −0.15, foot 0.2, torso about 0.06) so they satisfy this and don't fight each other at the joint limit.
- **Gains:** sized for the joints' large armature (about 1 kg·m²) and the 0.008 s control period, giving roughly 20 rad/s bandwidth with damping ratio about 0.6–0.9 and no discrete-time instability.
- **Start-up:** the phase starts at 3.6 rad, so the first movement is a gentle crouch rather than a push-off from a standing start.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.6}],
 "bias": {"a0": 0.18, "a1": -0.225, "a2": -0.02},
 "units": [
   {"type": "linear", "name": "torso_balance_speed",
    "inputs": {"obs[1]": -3.0, "obs[7]": -0.25, "obs[5]": -0.15},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm",
    "inputs": {"obs[3]": -1.5, "obs[9]": -0.15, "sin(P)": 0.5},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance",
    "inputs": {"obs[4]": -1.0, "obs[10]": -0.1, "obs[5]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "toe_pushoff",
    "inputs": {"cos(P)": -0.479, "sin(P)": 0.878},
    "threshold": 0.3, "sharpness": 4.0, "to": {"a2": -0.3}}
 ]}
```

The ankle-balance target contributes +0.28 to a2. The toe-pulse resting offset (+0.3) is cancelled by −0.3, so the a2 bias is −0.02.