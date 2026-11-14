I couldn't run anything, so this is a conservative hand-tuned controller. It tries to stand and balance rather than hop, since a stable stand earns about 1 point per step (up to roughly 1000). All the gains and the balance-term signs are untested guesses.

- **Thigh and leg:** a PD controller holds both joints at zero angle.
- **Foot:** a PD controller holds the foot joint at zero, plus a balance term. The balance term uses torso tilt, torso angular velocity and forward velocity to counter forward or backward falls.

```python
import numpy as np


def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, d1, d2, d3 = obs

    a1 = -6.0 * q1 - 0.3 * d1
    a2 = -6.0 * q2 - 0.3 * d2
    a3 = -2.0 * q3 - 0.1 * d3 + 3.0 * th + 0.5 * w + 0.2 * vx

    return [float(np.clip(a, -1.0, 1.0)) for a in (a1, a2, a3)]
```