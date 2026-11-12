The observation and health rules match a MuJoCo-style one-legged hopper (torso height, torso pitch, three joint angles, then velocities). A good hopping gait could beat standing, but I can't tune one without testing, and a gait that falls early scores far less. So this controller aims to stay healthy for all 1000 steps, which earns about 1000. It holds the leg stiff and upright with a joint PD controller, and the ankle gets extra feedback on torso pitch so the foot pushes back against any lean.

```python
import numpy as np

# Joint-space PD gains (action units per rad, per rad/s)
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.12, 0.12, 0.10])

# Extra torso-pitch feedback applied through the ankle
K_PITCH = 1.0
D_PITCH = 0.08


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    pitch = obs[1]
    q = obs[2:5]
    pitch_rate = obs[7]
    qd = obs[8:11]

    # Hold a rigid, straight posture
    a = -KP * q - KD * qd

    # Ankle balance: if torso leans forward (pitch > 0), press toe down,
    # which rotates the body back over the foot (and vice versa)
    a[2] += K_PITCH * pitch + D_PITCH * pitch_rate

    # Keep the upper joints from letting the torso drift
    a[0] += 0.5 * pitch + 0.05 * pitch_rate

    return [float(x) for x in np.clip(a, -1.0, 1.0)]
```