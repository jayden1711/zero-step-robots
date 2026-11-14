I couldn't run this, so it is untested. It's a hand-designed controller that tries to keep the hopper standing upright rather than hopping. If it holds balance for all 1000 steps, each episode scores about 1000. It earns nothing from forward velocity, but it avoids the much higher risk of an early fall that a hand-tuned gait would carry.

**How it works.** Three hidden units each compute one joint's torque before it is clipped. The output layer passes each unit straight through, and `tanh` saturates at ±1, the same limit as the action clip.

- **Hip (thigh joint):** keeps the torso upright. Torque = `2·torso_angle + 0.2·torso_angvel − 1·thigh − 0.1·thigh_vel`.
  - A positive hip torque pushes the torso forward by reaction.
  - So when the torso leans back (positive angle), the hip applies positive torque.
- **Knee (leg joint):** holds the leg straight. Torque = `0.3 − 2·leg − 0.1·leg_vel`.
  - The constant 0.3 presses the knee against its straight-leg limit at 0, which locks it.
- **Ankle (foot joint):** balances the whole body over the foot.
  - It applies a PD term on the foot joint, plus feedback on the leg's absolute angle (torso + thigh + leg) and its rate.
  - When the body leans forward, the ankle torque is negative, which pushes the body back over the foot.
- **Gains:** chosen against the actuator gear of 200. That gives enough stiffness to beat the gravity torque, and the damping is kept low enough to stay stable with the 0.008 s step.

```json
{
"W1": [
[0, 2.0, -1.0, 0, 0, 0, 0, 0.2, -0.1, 0, 0],
[0, 0, 0, -2.0, 0, 0, 0, 0, 0, -0.1, 0],
[0, 1.0, 1.0, 1.0, -2.0, 0, 0, 0.2, 0.2, 0.2, -0.1],
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
"b1": [0, 0.3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
"W2": [
[1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
],
"b2": [0, 0, 0]
}
```