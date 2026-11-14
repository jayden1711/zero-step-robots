This is a guessed controller, since I couldn't run anything. The observation layout looks like the standard Hopper: height, torso angle, three joint angles, velocities. I wrote a conservative balance controller that aims to stay upright for the full 1000 steps. Gains and sign conventions are untested.

```python
import numpy as np

def reset():
    pass

def act(obs):
    ang = obs[1]
    vx = obs[5]
    angvel = obs[7]
    knee = obs[3]
    knee_vel = obs[9]

    lean = ang + 0.1 * vx
    foot = -(6.0 * lean + 0.6 * angvel)
    thigh = -(4.0 * lean + 0.4 * angvel)
    leg = -(2.0 * knee + 0.1 * knee_vel)

    return [float(np.clip(thigh, -1, 1)),
            float(np.clip(leg, -1, 1)),
            float(np.clip(foot, -1, 1))]
```