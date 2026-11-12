The controller holds the hopper standing still instead of hopping. The goal is to survive all 1000 steps, which gives about 1000 reward per episode with almost no risk.

**Why this works:** In its initial pose, the hopper's center of mass sits over its flat foot, which spans x from −0.13 to 0.26 around the ankle at x = 0. If every joint is held rigidly, the robot acts like a rigid body resting on a flat base, and that is statically stable. With zero torque it falls only because the joints fold under gravity. So all the controller needs is a stiff, well-damped PD hold of each joint at 0.

**How the network does it:** Each of the first three hidden units computes `tanh(q_j + 0.1·q̇_j)` for one joint: thigh (obs 2 and 8), leg (obs 3 and 9) and foot (obs 4 and 10). Its output weight is −3, so near zero the torque is about −3·q − 0.3·q̇ in action units. With the gear ratio of 200, that is about 600 Nm/rad of stiffness and 60 Nm·s/rad of damping.
- The stiffness is well above the gravitational toppling stiffness, which is roughly 100 Nm/rad.
- The damping is close to critical for the knee and hip inertias.
- The gains stay small enough to be stable at the 0.008 s control step.

The thigh and leg joint limits (upper limit 0) also help hold the straight posture. All other weights and biases are zero.

```json
{
"W1": [
[0,0,1,0,0,0,0,0,0.1,0,0],
[0,0,0,1,0,0,0,0,0,0.1,0],
[0,0,0,0,1,0,0,0,0,0,0.1],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0]
],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[-3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-3,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```