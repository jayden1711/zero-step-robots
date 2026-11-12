This is a conservative balance controller. I couldn't run it, so it is untested. It aims to keep the hopper upright for the full 1000 steps (about 1000 reward) and makes no attempt to hop forward.

- **Thigh and leg:** a constant small positive torque (0.3) holds both joints against their straight limit, so the leg acts as a rigid pole.
- **Foot:** torque is proportional to torso angle (gain 2.0) plus torso angular velocity (gain 0.3). A forward lean pushes the body back.
- **Hidden units:** only two are used, scaled so tanh stays near-linear for normal angles. The other 14 are zeroed.

The foot-torque sign is derived by hand from the joint axis and could be wrong. If it is, the hopper falls and the score will be low.

```json
{
"W1": [
[0,0,0.5,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0.2,0,0],
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
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0]
],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[4.0,1.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0.3,0.3,0.0]
}
```