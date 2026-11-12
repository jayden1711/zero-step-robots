This is an untested controller. I'm treating the system as a Hopper-style robot (height, torso angle, three joint angles, then their velocities). It holds the three joints near zero with PD control, and the foot torque also leans against torso tilt. The torque signs and gains come from an assumed convention, so they may need tuning.

```python
import numpy as np


def reset():
    pass


def act(obs):
    theta = obs[1]
    q = obs[2:5]
    w = obs[7]
    qd = obs[8:11]

    a = -2.0 * np.array(q) - 0.1 * np.array(qd)
    a[2] += 1.5 * theta + 0.3 * w
    a[0] += 1.0 * theta + 0.15 * w
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
```