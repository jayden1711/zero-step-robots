This is a hand-tuned balance controller, untested, since I can't run anything. The observation layout looks like a Hopper-style system, which is my guess from the dimensions and termination rules. The controller keeps the torso upright and holds the joints near zero so the episode survives all 1000 steps, which is worth roughly 1000 reward. It doesn't try to chase forward speed. The ankle torque sign is based on reasoning about the joint axes, so it is the main risk.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q_thigh, q_leg, q_foot = obs[0], obs[1], obs[2], obs[3], obs[4]
    vx, vz, w_ang, w_thigh, w_leg, w_foot = obs[5], obs[6], obs[7], obs[8], obs[9], obs[10]

    foot = 8.0 * ang + 0.8 * w_ang - 0.3 * q_foot - 0.02 * w_foot
    thigh = -2.0 * q_thigh - 0.1 * w_thigh
    leg = -2.0 * q_leg - 0.1 * w_leg

    a = np.clip([thigh, leg, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```