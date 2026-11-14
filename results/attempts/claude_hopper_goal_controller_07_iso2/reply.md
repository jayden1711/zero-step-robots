This is an untested guess: I haven't run it, and the joint sign conventions are assumed. It's a stand-still balancer that holds the thigh and leg joints straight with PD control, and uses the foot joint to keep the torso upright. Since each step pays 1 for staying healthy, surviving 1000 steps is worth about 1000, while the forward-motion bonus is a minor extra. I assumed this is Hopper-like, with obs[0] the height, obs[1] the torso angle, obs[2:5] the joint angles, obs[5:8] the body velocities and obs[8:11] the joint velocities.

```python
import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q_th, q_leg = obs[2], obs[3]
    w = obs[7]
    qd_th, qd_leg = obs[8], obs[9]

    a_th = 0.1 - 5.0 * q_th - 0.3 * qd_th
    a_leg = 0.1 - 5.0 * q_leg - 0.3 * qd_leg
    a_ft = 5.0 * ang + 0.5 * w - 0.3 * obs[5]

    return [float(np.clip(a_th, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_ft, -1, 1))]
```