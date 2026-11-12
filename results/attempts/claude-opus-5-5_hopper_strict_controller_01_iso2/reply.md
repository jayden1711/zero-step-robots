This looks like the classic one-legged hopper. Here is how I read the observation:

- obs[0] is the torso height.
- obs[1] is the torso pitch.
- obs[2:5] are the hip, knee and ankle joint angles.
- obs[5:11] are the velocities.

I couldn't run anything, so this is a guess about the dynamics. If the guess is right, the controller earns about 1 point per step for 1000 steps, roughly 1000 per episode. Any forward speed adds to that.

A hopping gait would score more, but writing one blind is very likely to fall over early and score far less. So the controller only tries to stand still and stay healthy for the full 1000 steps:

- **How it stands:** each joint is held at angle 0 by a stiff PD controller. When all joints are at zero, the links should be stacked vertically with the foot flat on the ground. The centre of mass would then sit over the foot, so the body balances on its own like a rigid object.
- **Correction terms:** two small terms push the torso back toward upright and damp drift. They are kept small on purpose, because I couldn't check which way the signs act.
- **Gains:** I chose them to stay numerically stable. That assumes large joint armature, which is my guess about the model.

```python
import numpy as np

KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.3, 0.3, 0.3])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]

    # PD hold every joint at zero (straight, upright leg, flat foot)
    a = -KP * q - KD * qd

    # Small torso-upright correction through the hip
    pitch = o[1]
    pitch_rate = o[7]
    a[0] += 0.5 * pitch + 0.05 * pitch_rate

    return [float(x) for x in np.clip(a, -1.0, 1.0)]
```