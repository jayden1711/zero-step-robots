This looks like a Hopper-style system. I couldn't run it, so the gains are untested estimates. The controller holds the thigh and leg joints near straight with PD feedback and balances with ankle torque from the body pitch angle and its rate.

```python
import numpy as np

def reset():
    pass

def act(obs):
    ang = obs[1]
    q_th, q_leg, q_ft = obs[2], obs[3], obs[4]
    vx = obs[5]
    w = obs[7]
    d_th, d_leg, d_ft = obs[8], obs[9], obs[10]

    a_th = -5.0 * q_th - 0.3 * d_th
    a_leg = -5.0 * q_leg - 0.3 * d_leg
    a_ft = 3.0 * ang + 0.6 * w + 0.1 * vx - 0.5 * q_ft - 0.05 * d_ft

    return [float(np.clip(a_th, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_ft, -1, 1))]
```