This is my best guess without being able to run anything, so I haven't tested it. The observation layout matches a Hopper-style one: `obs[0]` is height, `obs[1]` is torso pitch, `obs[2:5]` are the thigh, leg and foot joint angles, and `obs[5:]` are velocities.

The controller stays upright and does not try to run:

- **Thigh and leg:** a constant push toward the straight-leg joint limit, so the leg stays locked straight.
- **Foot:** a PD feedback on torso pitch, plus a small term on forward speed, acting like an inverted-pendulum balance at the ankle.

The sign of the foot feedback is inferred from the joint axes, not checked in simulation. If it is wrong, the hopper would fall almost immediately.

```python
import numpy as np


def reset():
    pass


def act(obs):
    angle = obs[1]
    vx = obs[5]
    angvel = obs[7]
    foot = 10.0 * angle + 1.0 * angvel + 0.3 * vx
    foot = float(np.clip(foot, -1.0, 1.0))
    return [1.0, 1.0, foot]
```