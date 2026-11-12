This design uses no oscillators. It relies on body feedback and a hop reflex triggered by vertical velocity.

**Sign conventions.** The torso (rooty), thigh, leg and foot joints all use axis (0, -1, 0). For each joint, a positive angle moves the lower end of the child segment toward +x. For the foot, a positive angle lifts the toe.

**Control laws**

- **Hip (a0): keep the torso level.** The hip applies `a0 = 1.8·(θ_torso + 0.12·θ̇_torso)`. The torso is light compared with the leg and foot. So this torque mostly turns the torso, whether the foot is on the ground or in the air. Its damping ratio is about 0.8. This guards the |angle| < 0.2 limit.
- **Knee (a1): keep the leg straight and stiff.** A stiff controller holds the knee near its 0 limit, with a small extending bias. The leg then acts like a rigid strut, so the height stays well above 0.7.
- **Ankle (a2): balance and speed, using the long foot.**
  - A spring-damper on the foot angle sets the lean of the whole body while the foot is flat. Its stiffness of about 200 Nm/rad is greater than the tipping effect of gravity, about 80 Nm/rad.
  - In flight, the same term turns the foot back to its target angle, so it lands roughly flat.
  - A constant bias of +0.15 leans the body forward. A forward-velocity term of −0.15·v pulls the lean back as speed rises, so the target speed is about 1 m/s.
- **Hop reflex.** The ankle gets `−0.6·tanh(10·ż)`. While the body rises, the toe pushes down hard, enough to lift the heel and leave the ground. While it falls, the foot is pulled toe-up.
  - This acts as a bang-bang engine that pumps energy into each hop. Each landing restarts the push, so the hop rhythm follows the actual contact timing rather than a fixed clock.
  - The toe push also pitches the body backward in flight. That brings the foot forward under the centre of mass for the next landing, so a forward lean turns into steady forward hopping.

This is a principled guess, not a tested controller; I could not simulate it.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [],
 "couplings": [],
 "bias": {"a1": 0.05, "a2": 0.15},
 "units": [
   {"type": "linear", "name": "hip_torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.12},
    "range": 0.6, "tol": 0.05, "to": {"a0": 1.8}},
   {"type": "linear", "name": "knee_straight_pd", "inputs": {"obs[3]": -1.0, "obs[9]": -0.05},
    "range": 0.3, "tol": 0.05, "to": {"a1": 3.0}},
   {"type": "linear", "name": "ankle_lean_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.12},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "speed_regulation", "inputs": {"obs[5]": 1.0},
    "range": 2.5, "tol": 0.05, "to": {"a2": -0.15}},
   {"type": "reflex", "name": "hop_push", "inputs": {"obs[6]": 1.0}, "threshold": 0.0,
    "sharpness": 10.0, "to": {"a2": -0.6}}
 ]}
```