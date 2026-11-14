This controller is untested. It is a hand-designed PD stabiliser that assumes the obs layout is Hopper-style (torso angle at index 1, joint angles at 2 to 4, angular velocities at 7 to 10). I made the signs and gains judgement calls and did not verify them. It aims to stay upright for the full 1000 steps rather than to run fast.

- **Foot torque:** pushes against torso tilt and tilt rate.
- **Thigh torque:** also corrects tilt, and holds the thigh near zero.
- **Leg torque:** holds the leg joint stiff.

```json
{
"W1": [
[0,5,0,0,-0.5,0,0,0.5,0,0,-0.1],
[0,3,-1,0,0,0,0,0.3,-0.1,0,0],
[0,0,0,-3,0,0,0,0,0,-0.1,0],
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
[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```