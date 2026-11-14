This is a stability-first controller. Nothing has been run or tested.

The observation layout looks like a Hopper-style planar one-legged robot. I'm assuming obs[0] is torso height, obs[1] is torso pitch, obs[2:5] are the hip, knee and ankle angles, and obs[5:8] are body velocities, with joint rates after that. Under that guess, the controller aims to stay upright for the full 1000 steps (about 1000 reward) rather than chase forward speed, which is risky without testing.

- **Ankle:** pushes against torso lean using the pitch and its rate. I inferred the sign (a positive pitch means leaning backward, so a positive ankle torque corrects it) from the assumed joint axes, so that sign is the main risk.
- **Hip and knee:** hold their joint angles near zero with a soft PD law so the leg doesn't collapse.

```python
import numpy as np


def reset():
    pass


def act(obs):
    q0 = obs[1]      # torso pitch
    q1 = obs[2]      # hip
    q2 = obs[3]      # knee
    w0 = obs[7]      # pitch rate
    w1 = obs[8]
    w2 = obs[9]

    a3 = 5.0 * q0 + 0.5 * w0
    a1 = -2.0 * q1 - 0.1 * w1
    a2 = -2.0 * q2 - 0.1 * w2

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
```