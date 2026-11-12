This is an untested balance controller: it aims to stay upright and alive for the full 1000 steps rather than hop forward. I've assumed the observation layout of a Hopper-style robot (torso height, torso angle, three joint angles, then velocities). The feedback signs come from reasoning about torque reactions, not from a simulation run, so they may be wrong.

```python
import numpy as np

def reset():
    pass

def act(obs):
    ang = obs[1]
    q_thigh, q_knee, q_foot = obs[2], obs[3], obs[4]
    vx = obs[5]
    w = obs[7]
    dth, dkn, dft = obs[8], obs[9], obs[10]

    lean = ang + 0.1 * vx
    foot = 2.0 * lean + 0.3 * w - 0.2 * dft
    thigh = 1.0 * lean + 0.15 * w - 0.02 * dth
    knee = -0.5 * q_knee - 0.05 * dkn

    a = np.clip([thigh, knee, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```