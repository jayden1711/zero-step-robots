This controller is built to stand still and balance. It does not try to hop. A stable stand earns about 1 per step for all 1000 steps, so roughly **1000 per episode**. A hand-written hopping gait would probably fall early and score less.

**Why standing works:** With all joints held at 0, the hopper is a rigid column standing on its foot. The foot reaches from x ≈ −0.13 to +0.26, and the robot's center of mass sits at about x ≈ 0.02. That is well inside the foot, so the robot is statically stable. The starting perturbations (at most 0.005) are too small to tip it.

**Controller:** Each joint gets a spring-and-damper (PD) controller that pulls it back to angle 0: `a = -5·q - 0.5·q̇`. With the 200× motor gear, that is a stiffness of 1000 Nm/rad and damping of 100 Nms/rad.
- The joints have an armature of 1, so their effective inertia is at least 1 kg·m².
- With the 0.008 s control step, that keeps `Kd·dt/I ≈ 0.8`, below the instability limit of 2.

The foot also gets a small extra term that pushes the torso back upright: `-2·θ - 0.2·θ̇`. Every hidden tanh unit is scaled by 0.1 so it works in its near-linear range, and the output weights scale the signals back up.

```json
{
  "W1": [
    [0, 0, 0.1, 0, 0, 0, 0, 0, 0.01, 0, 0],
    [0, 0, 0, 0.1, 0, 0, 0, 0, 0, 0.01, 0],
    [0, 0, 0, 0, 0.1, 0, 0, 0, 0, 0, 0.01],
    [0, 0.1, 0, 0, 0, 0, 0, 0.01, 0, 0, 0],
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
    [-50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, -50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, -50, -20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b2": [0, 0, 0]
}
```