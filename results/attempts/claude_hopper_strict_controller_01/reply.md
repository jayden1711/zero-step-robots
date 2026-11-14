I can't run or test anything here, so this controller is a hand-designed balance stabilizer, not a tuned or verified one. The sign conventions and gains come from assuming a Hopper-style model. Treat it as a best guess aimed at surviving the full 1000 steps.

The 11 observations look like a Hopper: `obs[0]` is torso height, `obs[1]` is torso pitch, `obs[2:5]` are the thigh, leg and foot joint angles, `obs[5:8]` are the torso's translational and angular velocities, and `obs[8:11]` are the joint velocities. The controller reads the signs as follows:

- **Foot (ankle):** positive pitch means leaning forward, so it pushes the foot toward toe-up, which rotates the body back. The gains are modest.
- **Thigh and leg:** PD hold near zero joint angle, keeping the posture stable.
- **Forward progress:** none. I'm prioritizing staying healthy for 1000 steps, which earns about 1 point per step, over speed, which I can't tune blind.

```python
import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q_thigh, q_leg, q_foot = obs[2], obs[3], obs[4]
    w = obs[7]
    dq_thigh, dq_leg, dq_foot = obs[8], obs[9], obs[10]

    a_thigh = -2.0 * q_thigh - 0.05 * dq_thigh + 1.0 * ang + 0.1 * w
    a_leg = -2.0 * q_leg - 0.05 * dq_leg
    a_foot = 4.0 * ang + 0.4 * w - 0.3 * dq_foot

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```