I couldn't run anything, so this controller is a conservative guess. It tries to stand still and balance, which should earn roughly 1 reward per step if it works. It holds the thigh and leg joints straight with a PD controller. It also uses the foot torque to counter torso lean, and the sign of that correction is inferred from the joint axis conventions. The gains are kept low to avoid discrete-time instability.

```python
import numpy as np

def reset():
    pass

def act(obs):
    z, th, q1, q2, q3, vx, vz, w, w1, w2, w3 = obs
    a1 = -3.0 * q1 - 0.1 * w1
    a2 = -3.0 * q2 - 0.1 * w2
    a3 = 4.0 * th + 0.4 * w - 0.5 * q3 - 0.03 * w3
    return [float(np.clip(a1, -1, 1)), float(np.clip(a2, -1, 1)), float(np.clip(a3, -1, 1))]
```