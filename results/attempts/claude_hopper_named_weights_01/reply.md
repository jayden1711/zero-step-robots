This controller is a hand-designed joint-holding PD controller. I couldn't run or test it, so its score is a guess.

Each of the first three hidden units reads one joint's angle and angular velocity, and its output torque opposes both. That tries to keep the leg straight so the hopper stays upright. The other 13 hidden units are zeroed out.

The controller has no torso-balance feedback, because I couldn't be sure of the sign convention for the torso angle. The hopper may therefore still tip over before 1000 steps. It also has no deliberate forward-motion term, so I expect it to earn mostly the survival reward.

```json
{
"W1": [
[0,0,3,0,0,0,0,0,0.2,0,0],
[0,0,0,3,0,0,0,0,0,0.2,0],
[0,0,0,0,3,0,0,0,0,0,0.2],
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
[-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```