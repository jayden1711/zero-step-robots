This is an untested, survival-first controller. I couldn't run anything, so the gains are estimates. I did not try to build a hopping gait.

- **Thigh and leg:** a stiff PD controller holds both joints near zero, which keeps the leg straight like a rigid pole.
- **Ankle:** feedback on torso angle and angular velocity balances the pole on the foot. The sign follows from the joint axes: all four joints rotate about -y, so a positive torso angle is a backward lean, and a positive foot torque pushes the top of the body forward.
- **Expected score:** about 1000 if it stays upright for the full 1000 steps (1 per step plus a small forward-velocity term), minus a small action cost.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q1, q2, q3, vx, vz, w, w1, w2, w3 = [float(v) for v in obs]

    a1 = -3.0 * q1 - 0.2 * w1
    a2 = -3.0 * q2 - 0.2 * w2
    a3 = 1.5 * ang + 0.25 * w - 0.5 * q3 - 0.05 * w3

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
```