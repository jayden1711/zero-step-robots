I've written this controller from first principles without any testing. It holds the leg joints straight against their stops and balances the torso with the ankle. Its aim is to survive all 1000 steps (about 1000 reward) rather than to run fast.

The observation and action layout matches a Hopper-style model, and the controller depends on these assumptions:
- All joint axes point the same way (`-y`), so a positive foot action pushes the torso toward a smaller `obs[1]` when `obs[1]` is positive.
- The thigh and leg joints have an upper limit of 0 (straight), so a positive torque on them presses against the stop.

If either assumption is wrong, the controller will fail.

```python
import numpy as np


def reset():
    pass


def act(obs):
    angle = obs[1]
    angvel = obs[7]
    ankle = 4.0 * angle + 0.6 * angvel
    ankle = float(np.clip(ankle, -1.0, 1.0))
    return [0.5, 0.5, ankle]
```