This controller is a hand-built guess. I couldn't run or test anything, so the gains and signs come from reasoning about the joint axes, not from simulation. It aims to keep the hopper standing upright, which earns about 1 reward per step, and it makes no attempt to hop forward.

Only three of the 16 hidden units are used; the other 13 have zero weights. Each used unit stays near its linear range for typical observations.

- **Unit 0, torso pitch:** feeds the hip torque as a PD term on torso angle and angular velocity.
- **Unit 1, height:** drives the knee to extend when the torso is below about 1.25 m. A bias of +0.3 on the knee output offsets gravity.
- **Unit 2, foot:** applies a damped restoring torque to the foot joint.

```json
{
"W1": [
[0,1.0,0,0,0,0,0,0.1,0,0,0],
[1.0,0,0,0,0,0,0.1,0,0,0,0],
[0,0,0,0,0.5,0,0,0,0,0,0.05],
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
"b1": [0,-1.25,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-2,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0.3,0]
}
```