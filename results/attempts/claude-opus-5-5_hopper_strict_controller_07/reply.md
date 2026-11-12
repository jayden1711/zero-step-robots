This is a standing-balance controller. I couldn't test it, and it gives up forward speed to survive.

The 11-number observation and the health rules match a planar one-legged hopper:

- **Observation:** height (`obs[0]`), torso angle (`obs[1]`), three joint angles (hip, knee, ankle, `obs[2:5]`), then their velocities (`obs[8:11]`).
- **Starting pose:** upright with the leg straight, which is the knee's joint limit, and the foot flat.

**Strategy:** A hopping gait could earn more than 1000 but is easy to get wrong blind, and an early fall loses most of the episode. So the controller holds every joint stiffly at its starting angle with a PD law. The body then acts as one rigid piece standing on a flat foot. Its centre of mass sits over the foot, so it should stay standing.

**Expected score:** about 1000, i.e. roughly +1 per step for 1000 steps. Forward speed adds little, and the action penalty is negligible.

**Gains:** The stiffness and damping are moderate. They are strong enough to hold the pose against gravity, but low enough that the damping term stays stable with the 0.008 s step. The outputs are clipped to [-1, 1] to keep the action penalty predictable.

```python
import numpy as np

# Joint PD gains (action units per rad and per rad/s; torque = 200 * action)
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.10, 0.10, 0.10])
TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    a = KP * (TARGET - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```