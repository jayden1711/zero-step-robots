This looks like a Hopper-style robot (torso height, torso pitch, three joint angles, then velocities). I could not run anything, so this controller only tries to stay upright for the full 1000 steps and does not try to hop forward. The sign conventions are inferred from the standard Hopper model, not tested.

- **Foot:** a PD controller on torso pitch, with negative feedback.
- **Thigh and knee:** a small constant torque toward the straight-leg position, plus damping, to hold height.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, th = obs[0], obs[1]
    qt, ql, qf = obs[2], obs[3], obs[4]
    w = obs[7]
    dt_, dl, df = obs[8], obs[9], obs[10]

    a_foot = -(2.0 * th + 0.25 * w) - 0.3 * qf - 0.02 * df
    a_thigh = 0.3 - 0.5 * dt_ * 0.1
    a_leg = 0.4 - 0.5 * dl * 0.1

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_foot, -1, 1))]
```