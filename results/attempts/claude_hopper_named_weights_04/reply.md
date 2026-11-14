I couldn't run or test anything, so this is a hand-designed stabilizing controller, not a tuned one. Three of the 16 hidden units are active and the rest are zero.

- **Thigh torque:** a PD term on torso angle and angular velocity, assuming a positive torso angle means leaning backward. I haven't verified that sign.
- **Leg torque:** a PD term that holds the leg joint near zero.
- **Foot torque:** a small term on torso angle and angular velocity.

```json
{
  "W1": [
    [0,4,0,0,0,0,0,0.4,0,0,0],
    [0,0,0,-3,0,0,0,0,0,-0.2,0],
    [0,2,0,0,0,0,0,0.2,0,0,0],
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
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0.5,0,0,0,0,0,0,0,0,0,0,0,0,0]
  ],
  "b2": [0,0,0]
}
```