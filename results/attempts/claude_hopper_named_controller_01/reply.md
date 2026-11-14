I couldn't run anything, so this is an untested controller. It uses PD feedback to keep the torso upright, with the leg held extended to maintain height.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, dq1, dq2, dq3 = [float(v) for v in obs]

    # Lean target: damp horizontal drift slightly, allow a small forward bias.
    th_err = th + 0.05 * vx - 0.02

    # Thigh: reaction torque on the torso corrects pitch.
    a0 = 4.0 * th_err + 0.5 * w

    # Leg: keep extended, push harder when sagging.
    a1 = 0.3 + 2.0 * (1.2 - z) - 0.05 * dq2

    # Foot: ankle assists balance and stays near neutral.
    a2 = 2.0 * th_err + 0.3 * w - 0.5 * q3 - 0.05 * dq3

    return [float(np.clip(a0, -1, 1)),
            float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1))]
```

The torque signs come from reasoning about joint reaction forces, not from simulation, so a sign error would make it fall quickly. If it does, flipping the sign of the `th_err` terms in `a0` and `a2` is the first thing to try.