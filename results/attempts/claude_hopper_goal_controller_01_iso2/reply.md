I couldn't run anything, so this is a conservative balance controller built on a guess about the system. The 11-number observation, 3 torques and health limits look like a Hopper-style one-legged walker, so I assumed that layout:

- **Layout:** obs[0] is torso height, obs[1] is torso pitch, obs[2:5] are the thigh, leg and foot joint angles, and obs[5:8] are x velocity, z velocity and pitch rate.
- **Strategy:** Surviving all 1000 steps is worth about 1000 reward, so the controller just stays upright rather than chasing speed.
- **Ankle feedback:** The foot joint torque is PD feedback on torso pitch.
- **Hold posture:** Thigh and leg joints are lightly damped back toward their zero pose.
- **Risk:** The sign of the ankle feedback is the main uncertainty. If forward and backward lean are the opposite way round from what I assumed, it will destabilise instead of balance.

```python
import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    angvel = obs[7]
    foot = 2.0 * ang + 0.4 * angvel + 0.3 * obs[5] * 0.0
    thigh = -1.0 * obs[2] - 0.1 * obs[8]
    leg = -1.0 * obs[3] - 0.1 * obs[9]
    a = np.clip([thigh, leg, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```