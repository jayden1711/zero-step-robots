I wrote a hand-designed stabilizer rather than a trained policy, since I can't run anything here. It is untested, and its sign conventions come from my assumptions about the system, not from checking.

I'm assuming the observation layout of a Hopper-style system: height, torso angle, three joint angles, then velocities. The foot torque leans against the torso angle and angular velocity. The thigh and leg get mild PD damping toward zero. The aim is to stay healthy for the full 1000 steps, with forward progress as a bonus.

```json
{
  "W1": [
    [0,2.5,0,0,0,0,0,0.25,0,0,0],
    [0,0,-0.5,0,0,0,0,0,-0.05,0,0],
    [0,0,0,-0.5,0,0,0,0,0,-0.05,0],
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
    [0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  ],
  "b2": [0,0,0]
}
```