The controller tries to stand upright and balance for the full 1000 steps. That should score about 1000 per episode. I didn't attempt a hand-designed hopping gait: it is very hard to get right without testing, and an early fall would score far less.

Three of the hidden tanh units act as PD (spring-and-damper) controllers. Their inputs are scaled small so tanh stays roughly linear, and W2 scales the output back up by 10. The other 13 units are zero.

- **Hip (unit 0):** keeps the torso upright, `a0 ≈ 2·θ_torso + 0.2·ω_torso`. A positive hip torque pushes the torso angle back toward zero, whichever way the joint axis points.
- **Knee (unit 1):** keeps the leg straight, `a1 ≈ −3·q_leg − 0.3·q̇_leg`, plus a small positive bias of 0.05 that holds the knee against its straight-leg limit.
- **Ankle (unit 2):** `a2 ≈ −5·q_foot − 0.8·q̇_foot`. While the foot is flat, the foot joint angle is the negative of the leg's lean from vertical. This term therefore balances the body like an inverted pendulum pivoting at the ankle.
- **Why these gains:** the ankle stiffness (about 1000 N·m/rad at gear 200) is well above the gravity torque that tips the body over (about 100 N·m/rad). The damping is roughly critical for each joint.

```json
{
  "W1": [
    [0, 0.2, 0, 0, 0, 0, 0, 0.02, 0, 0, 0],
    [0, 0, 0, -0.3, 0, 0, 0, 0, 0, -0.03, 0],
    [0, 0, 0, 0, -0.5, 0, 0, 0, 0, 0, -0.08],
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
    [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b2": [0, 0.05, 0]
}
```