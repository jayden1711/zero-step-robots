I couldn't run or test anything, so this is a hand-designed stabilizing controller and not a tuned one. It holds the thigh, leg and foot joints near zero with PD feedback, and uses the foot torque to counter torso lean. The lean-correction sign is my best guess from the joint axis conventions. I expect it to stay up for some time and score roughly 1 reward per step, with no real forward drive.

```json
{
"W1": [
[0,5,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0.5,0,0,0],
[0,0,5,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0.3,0,0],
[0,0,0,5,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0.3,0],
[0,0,0,0,5,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0.3],
[0,0,0,0,0,0.5,0,0,0,0,0],
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
[0,0,-2,-1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,-2,-1,0,0,0,0,0,0,0,0,0,0],
[1.5,0.5,0,0,0,0,-0.5,-0.3,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```