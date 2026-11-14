This controller is untested, since I can't run anything here. It is a conservative balance controller that aims to keep the hopper upright for the full 1000 steps rather than hop fast.

The sign conventions come from the MuJoCo model, where all hinge axes are `0 -1 0`. A positive torso angle means leaning backward. A positive foot or thigh torque pushes the torso forward when the foot is planted. So the torso-angle feedback is positive on those two joints. The leg joint is held near straight with a PD term, and a small velocity term nudges the target lean forward to pick up some velocity reward.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q_thigh, q_leg, q_foot, vx, vz, w, w_thigh, w_leg, w_foot = obs

    vx_c = max(-1.0, min(1.0, vx))
    target = -0.03 - 0.02 * max(0.0, 1.0 - vx_c)
    err = ang - target

    foot = 6.0 * err + 0.8 * w
    thigh = 3.0 * err + 0.4 * w - 0.5 * q_thigh - 0.05 * w_thigh
    leg = -3.0 * q_leg - 0.3 * w_leg

    return [float(np.clip(thigh, -1, 1)),
            float(np.clip(leg, -1, 1)),
            float(np.clip(foot, -1, 1))]
```