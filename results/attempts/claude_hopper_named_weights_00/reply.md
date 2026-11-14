This is an untested hand-designed controller, since I can't run anything. It is a posture-holding PD controller built from three tanh units operating in their near-linear range, so it should keep the hopper upright but won't hop forward fast.

- **Thigh and leg:** PD feedback toward the straight posture (action ≈ -2·angle - 0.1·velocity).
- **Foot:** ankle balancing on torso tilt (action ≈ 4·torso angle + 0.5·torso angular velocity, with a small foot-joint damping term). I assumed that positive tilt means leaning forward, and that positive foot torque pushes the torso back.

```json
{
"W1": [
[0,0,-1,0,0,0,0,0,-0.05,0,0],
[0,0,0,-1,0,0,0,0,0,-0.05,0],
[0,2,0,0,-0.5,0,0,0.25,0,0,-0.025],
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
[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```