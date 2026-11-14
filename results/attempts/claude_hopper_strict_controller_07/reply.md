I can't run anything here, so this is an untested hand-built balance controller, and the signs are my best reading of the usual layout for this kind of system. If the observation matches a standard hopper (height, body angle, three joint angles, then velocities), the plan is to hold the leg straight and use the ankle torque to correct body tilt, so it survives long enough to collect the +1 per step.

```python
import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    thigh = obs[3 - 1 + 0] if False else obs[2]
    leg = obs[3]
    foot = obs[4]
    angvel = obs[7]
    thigh_v = obs[8]
    leg_v = obs[9]
    foot_v = obs[10]

    a_thigh = -2.0 * thigh - 0.1 * thigh_v + 0.3
    a_leg = -2.0 * leg - 0.1 * leg_v + 0.3
    a_foot = 3.0 * ang + 0.3 * angvel - 1.0 * foot - 0.05 * foot_v

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_foot, -1, 1))]
```

Index assumptions: obs[0] is height, obs[1] is body angle, obs[2:5] are thigh, leg and foot angles, and obs[5:11] are velocities (x, z, angular, then the three joints). The ankle gain signs are the part most likely to be wrong; if the tilt correction is backwards, the system will fall quickly.