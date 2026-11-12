This is a best-guess controller, since I can't run anything. It assumes the observation layout matches a standard 3-actuator hopper, with torso height, torso angle, three joint angles, then velocities. It tries to stand upright for the full 1000 steps (about 1000 reward) rather than risk falling while chasing forward speed.

It works in two parts:
- **Balance:** the ankle and hip torques are driven by the torso angle and its rate.
- **Joint hold:** the knee and the joints get a small restoring term.

The signs of the balance terms are my best inference, and I couldn't test them.

```python
import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q_thigh, q_leg, q_foot = obs[2], obs[3], obs[4]
    w = obs[7]
    dt, dl, df = obs[8], obs[9], obs[10]

    foot = 4.0 * ang + 0.5 * w - 0.3 * q_foot - 0.02 * df
    thigh = 2.0 * ang + 0.3 * w - 0.5 * q_thigh - 0.03 * dt
    leg = -1.0 * q_leg - 0.05 * dl

    a = np.clip([thigh, leg, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```