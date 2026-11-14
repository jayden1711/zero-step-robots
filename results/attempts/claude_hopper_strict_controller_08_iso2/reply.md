This looks like a Hopper-style system: the three actions are joint torques for hip, knee and ankle, and `obs[2:5]` are the joint angles. The controller holds the straight-standing posture with a stiff PD loop on each joint so the body doesn't collapse. That should earn the +1 per step for all 1000 steps. I couldn't run it, so the gains are estimates, and I didn't add torso-tilt feedback because I couldn't verify its sign blind.

```python
import numpy as np

KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.12, 0.12, 0.12])


def reset():
    pass


def act(obs):
    q = np.array(obs[2:5], dtype=float)
    qd = np.array(obs[8:11], dtype=float)
    a = -KP * q - KD * qd
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
```