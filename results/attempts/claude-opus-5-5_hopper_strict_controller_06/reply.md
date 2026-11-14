The observation and action layout matches MuJoCo **Hopper**: torso height, torso pitch, and thigh/leg/foot joint angles, then their velocities. I can't test anything, so I chose a conservative balance controller over a hopping gait. A hopping gait could score higher (around 3000), but tuned blind it would likely fall early and score far less. Standing upright for all 1000 steps should give about 1000.

How it works (the signs follow from all joints sharing one rotation axis, so it doesn't matter which way that axis points):
- **Hip:** pushes against the torso to keep the pitch `obs[1]` near 0 (the healthy limit is ±0.2).
- **Knee:** holds the leg straight against its joint limit.
- **Ankle:** keeps the rigid thigh+leg segment upright over the foot, like balancing an inverted pendulum. Ankle torque is kept small (clipped to ±0.35) so the toe or heel doesn't lift.
- A small term on forward velocity damps any drift.

```python
import numpy as np


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    r, t, l, f = o[1], o[2], o[3], o[4]
    vx = o[5]
    dr, dt_, dl, df = o[7], o[8], o[9], o[10]

    # Hip: keep torso pitch at zero (torso receives the reaction torque)
    a_hip = 1.0 * r + 0.12 * dr

    # Knee: hold straight (at upper joint limit 0)
    a_knee = -1.0 * l - 0.1 * dl + 0.05

    # Ankle: keep absolute leg angle (rigid thigh+leg segment) upright over the foot
    alpha = r + t + l
    dalpha = dr + dt_ + dl
    a_ankle = 1.0 * alpha + 0.3 * dalpha
    # damp horizontal drift (sign-agnostic small term: oppose motion via lean)
    a_ankle += 0.0 * vx
    a_ankle = float(np.clip(a_ankle, -0.35, 0.35))

    a = np.clip([a_hip, a_knee, a_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```

I set the drift term's gain to 0 because I can't confirm the sign of `obs[5]` relative to lean without testing, and a wrong sign would make the hopper less stable. In practice, the controller relies only on the angle and angular-velocity feedback.