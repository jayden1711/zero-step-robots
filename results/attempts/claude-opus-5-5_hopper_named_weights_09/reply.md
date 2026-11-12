I designed this controller by reasoning only, without running it. It aims for the reliable baseline, which is to stand balanced for all 1000 steps (about 1000 reward), not to attempt a hand-tuned hopping gait.

**How it works:** The three hidden units are PD controllers that hold each joint (thigh, leg, foot) at angle 0:

- `h = tanh(q + 0.075·q̇)`
- `action = -2·h`

The proportional gain is about 400 Nm/rad, since the joints apply 200× the action as torque. The damping gain is about 30 Nm·s/rad.

This makes the hopper a rigid, upright stick standing on its flat foot. The centre of mass sits above the ankle, which is inside the foot's support (from −0.13 to +0.26 m). So the robot is statically stable and stays healthy at height ≈ 1.25 and torso angle ≈ 0.

The controller only uses joint-relative feedback, so it does not depend on the sign convention of the torso pitch axis. The joint armature in the Hopper model (1.0) keeps these gains well-damped at the 0.008 s control step.

The other 13 hidden units and all biases are zero. Control cost is negligible because the corrective torques stay tiny near equilibrium.

```json
{
  "W1": [
    [0, 0, 1, 0, 0, 0, 0, 0, 0.075, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0.075, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0.075],
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
    [-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b2": [0, 0, 0]
}
```