This environment looks like a one-legged hopper (height, torso pitch, three joint angles, then velocities). Without any way to test, I chose the most reliable approach: hold the leg rigid and upright so the robot balances on its flat foot for all 1000 steps. That should score close to 1000. Hopping forward could score more, but a blind attempt would very likely fall early and score far less.

How it works:
- A stiff PD controller drives the three joint angles (obs[2:5]) to zero, damped by the joint velocities (obs[8:11]). This makes the body a rigid stack with its centre of mass over the foot, which is statically stable.
- Two small corrections use torso pitch (obs[1]) and its rate (obs[7]). One at the hip keeps the torso upright. One at the ankle shifts the body back over the foot if it starts to tip.
- The gains are moderate relative to the 0.008 s step, so the held control should not oscillate. The control cost is negligible.

```python
import numpy as np

# Joint PD gains (thigh, leg, foot)
KP = np.array([2.0, 2.0, 1.5])
KD = np.array([0.2, 0.2, 0.15])

# Small torso-pitch corrections
K_HIP_PITCH = 1.0
K_HIP_PITCH_D = 0.1
K_ANKLE_PITCH = 0.5
K_ANKLE_PITCH_D = 0.05


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    q = o[2:5]
    pitch_rate = o[7]
    qd = o[8:11]

    a = -KP * q - KD * qd

    # Hip: push the torso back toward upright (negative thigh torque reduces pitch)
    a[0] += -K_HIP_PITCH * pitch - K_HIP_PITCH_D * pitch_rate
    # Ankle: lean the body back over the foot if it tips
    a[2] += -K_ANKLE_PITCH * pitch - K_ANKLE_PITCH_D * pitch_rate

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```