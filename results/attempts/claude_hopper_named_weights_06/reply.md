I couldn't run or test anything, so this is a hand-designed stabilizing controller rather than a trained one. It is untested, and the signs are reasoned from the joint geometry, so a flipped sign would make it fall. It aims to stay upright for the full 1000 steps, which earns roughly 1 reward per step, rather than to hop fast.

- **Torso balance:** unit 0 reads torso angle and angular velocity. It drives the thigh and foot torques to push back against forward lean.
- **Leg:** unit 1 acts as a PD hold on the leg joint to keep it straight.
- **Thigh:** unit 2 acts as a PD hold on the thigh joint.

```json
{
"W1": [
[0,5,0,0,0,0,0,0.5,0,0,0],
[0,0,0,-3,0,0,0,0,0,-0.3,0],
[0,0,-3,0,0,0,0,0,-0.3,0,0],
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
[0.8,0,0.5,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0.8,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```