This controller holds the hopper standing still. It does not try to hop forward.

**What it does:** Each joint (thigh, leg, foot) gets a proportional-derivative (PD) controller that holds it at its starting angle of 0. The thigh controller also gets a small extra signal from the torso angle, to keep the torso upright.

**Why standing should work:** In the starting pose, the centre of mass sits over the ankle. The flat foot reaches from about −0.13 to +0.26 m in x, so the ankle is well inside it. A hopper with its joints held stiff should therefore stand like a rigid body. Each standing step earns about +1, so 1000 steps should give a score of roughly 1000. Hand-designing a forward hopping gait without being able to test it would very likely fall over early and score less.

**How the network does it:** Three hidden units are used, one per joint. The other 13 have zero weights.
- Thigh unit: −2·q_thigh − 0.2·q̇_thigh + 1.0·θ_torso + 0.1·θ̇_torso
- Leg unit: −2·q_leg − 0.2·q̇_leg
- Foot unit: −2·q_foot − 0.2·q̇_foot
- Each unit passes straight through to its own torque with weight 1. For small errors tanh is nearly linear, so this behaves like plain PD control. With the motor gear of 200, the gains come to about 400 Nm/rad and 40 Nms/rad.

```json
{
  "W1": [
    [0.0, 1.0, -2.0, 0.0, 0.0, 0.0, 0.0, 0.1, -0.2, 0.0, 0.0],
    [0.0, 0.0, 0.0, -2.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2, 0.0],
    [0.0, 0.0, 0.0, 0.0, -2.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ],
  "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "W2": [
    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ],
  "b2": [0.0, 0.0, 0.0]
}
```