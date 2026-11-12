I couldn't run or test any of this, so it's a conservative stabilizing controller. It holds the hopper upright to survive the full 1000 steps and doesn't attempt a hopping gait. I'm assuming the observation layout matches a standard Hopper: height, torso angle, three joint angles, then velocities.

```python
import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q0, q1, q2 = obs[2], obs[3], obs[4]
    angvel = obs[7]
    qd0, qd1, qd2 = obs[8], obs[9], obs[10]

    a0 = -4.0 * q0 - 0.3 * qd0
    a1 = -4.0 * q1 - 0.3 * qd1
    a2 = 4.0 * ang + 0.5 * angvel - 1.0 * q2 - 0.1 * qd2

    return [float(np.clip(a0, -1, 1)), float(np.clip(a1, -1, 1)), float(np.clip(a2, -1, 1))]
```

The knee and hip are held near zero with a PD loop. The ankle counters torso tilt, with the sign assumed from the standard joint axes. If that sign is wrong, the controller will likely fall quickly.