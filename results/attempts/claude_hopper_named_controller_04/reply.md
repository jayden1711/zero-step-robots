This is a conservative standing controller. I could not run it, so it is untested and I'm unsure of the sign convention for the balance term.

- **Thigh and leg:** a bias pushes both joints into their straight-leg limits (range -150° to 0°). A small PD term holds them at 0, so the leg acts as a rigid post.
- **Foot (ankle):** a PD balance term on torso angle and angular velocity. Positive torso angle is a backward lean, because the root hinge axis is `0 -1 0`. A positive foot action then applies a forward-leaning reaction torque, so the gain on the angle is positive.
- **Expected score:** about 1000 for staying upright, plus a small drift term and a negligible action cost. It does not aim for fast hopping, because I can't tune that without a simulator.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, dq1, dq2, dq3 = [float(v) for v in obs]

    a1 = 0.3 - 3.0 * q1 - 0.1 * dq1
    a2 = 0.3 - 3.0 * q2 - 0.1 * dq2

    a3 = 1.5 * th + 0.3 * w - 0.5 * q3 - 0.02 * dq3

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
```