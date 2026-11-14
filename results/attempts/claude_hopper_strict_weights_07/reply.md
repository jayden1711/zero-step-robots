I couldn't run or test anything here, so this controller is an untested guess. It assumes the standard Hopper layout: obs[1] is torso angle, obs[7] is its angular velocity, and positive actions lean the body forward. It applies PD feedback on torso angle and angular velocity to the hip and ankle torques. If those sign assumptions are wrong, it will fall quickly.

```json
{"W1":[[0,5,0,0,0,0,0,0.5,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]],
"b1":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2":[[1.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[1.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
"b2":[0,0,0]}
```