Approach: hold a rigid upright pose with PD control on each joint and collect the ~1 alive reward per step for all 1000 steps. I can't run anything, so I chose the safest strategy rather than attempting a hop.

**Design (three active hidden units, the other 13 are zeroed):**
- **Each unit is a PD term for one joint.** Unit *j* computes `h_j = tanh(Kp·q_j + Kd·q̇_j)`, and the output for that joint is `−h_j`.
- **Small-signal behaviour:** for small errors this is a linear PD with Kp = 2, giving about 400 N·m/rad through the gear of 200. Large errors saturate smoothly at the ±1 torque limit.
- **Hip and knee:** Kd = 0.1. The torso has low inertia about the hip, so higher damping risks discrete-time instability at dt = 0.008 s.
- **Ankle:** Kd = 0.3. The ankle stiffness of 400 N·m/rad is well above the gravity toppling stiffness of about 15 kg × 9.8 × 0.9 m ≈ 130 N·m/rad. With the foot flat, this keeps the whole rigid column upright over its foot.
- **No dependence on the torso-angle sign convention:** I used only joint-space feedback. A joint torque always pushes its own joint angle in the positive direction, so the controller does not depend on the root axis sign, which I can't verify.

Expected result: roughly 1000 per episode (alive bonus, minus a tiny control cost), assuming it stays balanced through the initial 4 cm drop onto the floor.

```json
{
  "W1": [
    [0, 0, 2.0, 0, 0, 0, 0, 0, 0.1, 0, 0],
    [0, 0, 0, 2.0, 0, 0, 0, 0, 0, 0.1, 0],
    [0, 0, 0, 0, 2.0, 0, 0, 0, 0, 0, 0.3],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "W2": [
    [-1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, -1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, -1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b2": [0, 0, 0]
}
```