This is an untested hand-written controller; I couldn't run it. I read the observation as a Hopper-style layout: `obs[0]` is torso height, `obs[1]` is torso pitch, `obs[2:5]` are the thigh, leg and foot joint angles, and `obs[5:11]` are the velocities (x, z, pitch, thigh, leg, foot).

The goal is mainly to stay alive for all 1000 steps, which earns about 1 per step.

- **Foot torque:** PD on torso pitch and pitch rate keeps the body balanced over the foot.
- **Thigh and leg:** held near neutral with damped PD so the leg doesn't buckle.
- **Forward speed:** a small bias term nudges the body slightly forward-leaning when slow, for the `v` reward, but balance is prioritized.

The sign of the foot-torque feedback comes from my reading of the joint axes, so it could be backwards if that reading is wrong.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, ang, th, lg, ft = obs[0], obs[1], obs[2], obs[3], obs[4]
    vx, vz, wang, wth, wlg, wft = obs[5], obs[6], obs[7], obs[8], obs[9], obs[10]

    a_foot = 2.5 * ang + 0.25 * wang - 0.05 * wft
    a_thigh = -1.0 * th - 0.1 * wth
    a_leg = -1.0 * lg - 0.1 * wlg

    # small damping of forward drift keeps balance; mild lean for speed
    a_foot += 0.15 * vx

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```