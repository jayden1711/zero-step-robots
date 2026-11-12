This is an untested standing-balance controller. I couldn't run it, so the gains and the sign conventions are my best judgement.

The thigh and leg joints are held straight with PD control toward their joint limits at 0. The foot joint does the balancing, using feedback on torso angle, angular velocity and forward velocity. The aim is to survive all 1000 steps, which earns about 1 point per step, rather than to run fast.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q1, q2, q3, vx, vz, wang, w1, w2, w3 = obs

    a1 = 0.3 - 3.0 * q1 - 0.1 * w1
    a2 = 0.3 - 3.0 * q2 - 0.1 * w2
    a3 = 3.0 * ang + 0.4 * wang + 0.15 * vx - 0.5 * q3 - 0.02 * w3

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
```