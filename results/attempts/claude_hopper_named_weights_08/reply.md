I couldn't run or test anything, so this is a hand-designed stabilizer, not a tuned gait. It uses one hidden unit to compute a torso-angle PD signal (angle plus angular velocity). That signal drives the ankle strongly and the hip more gently. A small constant positive torque on the knee holds the leg straight against its joint limit. The aim is to stay upright for the full 1000 steps and collect the survival reward. It won't earn much forward-velocity reward.

The sign convention (positive torso angle = leaning back, so positive torque corrects it) is inferred from how the model defines its joint axes, and I couldn't check it. If it's wrong, the controller will fall over quickly.

```json
{
"W1": [
[0,2.0,0,0,0,0,0,0.3,0,0,0],
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
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0]
],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[1.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[3.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0.3,0]
}
```