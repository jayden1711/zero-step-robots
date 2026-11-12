This is an untested controller. I can't run the simulation, so it only tries to keep the system upright for the full 1000 steps and does not try to hop forward. I read the observation as a hopper: height, torso angle, three joint angles, then velocities. I assumed the sign of the ankle torque from the joint axes, so if that sign is wrong it will fail.

- **Thigh and leg:** a PD controller holds each joint at zero angle, which keeps the body rigid.
- **Foot (ankle):** the torque is proportional to the torso angle and angular velocity. A forward lean produces a backward push on the body.

```python
import numpy as np

def reset():
    pass

def act(obs):
    ang = obs[1]
    q_thigh, q_leg = obs[2], obs[3]
    w_ang = obs[7]
    w_thigh, w_leg = obs[8], obs[9]

    a0 = -2.0 * q_thigh - 0.05 * w_thigh
    a1 = -2.0 * q_leg - 0.05 * w_leg
    a2 = -4.0 * ang - 0.4 * w_ang

    return [float(np.clip(a0, -1, 1)), float(np.clip(a1, -1, 1)), float(np.clip(a2, -1, 1))]
```