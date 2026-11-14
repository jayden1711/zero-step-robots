I couldn't run anything, so this is an untested hand-designed stabiliser, not a trained policy. Its aim is to keep the system upright for the full episode and collect the survival reward. The input roles below are my guess that this is a Hopper-style environment, and the feedback signs follow from that guess.

- **Controller:** one hidden unit reads the body angle (`obs[1]`) and its angular rate (`obs[7]`). That feeds torque to the thigh (action 0) and the foot (action 2) to push the lean back toward upright.
- **Other units and actions:** the leg action (action 1) and all other hidden units are zero.

If the sign guess is wrong, the controller will fall faster than doing nothing.

```json
{
  "W1": [
    [0,2.0,0,0,0,0,0,0.4,0,0,0],
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
    [2.5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [5.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  ],
  "b2": [0,0,0]
}
```