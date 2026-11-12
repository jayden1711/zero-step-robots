This is a 2D one-legged hopper. Its torso pitch is `obs[1]` (positive means leaning forward), the three joint angles are `obs[2:5]`, and their velocities are `obs[8:11]`. Since I can't test anything, I chose the most robust strategy rather than gambling on hopping: keep the robot standing upright and balanced on its foot for all 1000 steps. That earns about 1 reward per step, close to 1000 per episode. A failed hopping gait could fall over within tens of steps.

How it works:
- **Joints:** each joint uses moderate PD control toward 0, which keeps the leg straight. The gains are kept low so the 0.008 s control delay and the large actuator gear don't cause oscillation.
- **Torso:** the ankle and hip get extra feedback on torso pitch and pitch rate. If the body leans forward, the foot joint torque pulls the leg back over the foot, and the hip straightens the torso.
- **Action cost:** actions stay small, so the penalty is negligible.

```python
import numpy as np

KP = 1.0      # joint stiffness (action units per rad)
KD = 0.05     # joint damping
K_ANK = 3.0   # ankle feedback on torso pitch
K_ANK_D = 0.3
K_HIP = 1.0   # hip feedback on torso pitch
K_HIP_D = 0.1


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch, thigh, leg, foot = o[1], o[2], o[3], o[4]
    pitch_d = o[7]
    thigh_d, leg_d, foot_d = o[8], o[9], o[10]

    a_thigh = -KP * thigh - KD * thigh_d - K_HIP * pitch - K_HIP_D * pitch_d
    a_leg = -KP * leg - KD * leg_d
    a_foot = -KP * foot - KD * foot_d - K_ANK * pitch - K_ANK_D * pitch_d

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(x) for x in a]
```