The controller below aims to stand still and balanced for the full episode, which should score about 1000. It is not tuned for forward speed: a hopping gait could earn roughly 3000 or more, but I can't tune one without running it, and a hop that falls early would score much worse than standing.

How it works:

- **Why standing is stable:** The Hopper's foot reaches about 0.26 m in front of the ankle and 0.13 m behind it. With the body upright, the centre of mass sits about 0.13 m inside the back edge of the foot. If the joints are held stiff, the robot stands still.
- **Hip (thigh motor):** keeps the torso upright, using a PD loop on the torso's angle in the world. When the torso tilts back (positive angle), a positive hip torque pushes it forward.
- **Knee and ankle:** PD loops hold both joints straight (angle 0), so the leg stays vertical over the foot.
- **Forward drift:** the ankle also gets a small term from torso x-velocity. If the body starts tipping forward, the toe presses down and pushes it back.
- **Gain sizes:** Each motor has a gear ratio of 200, and each joint has armature 1, which adds at least 1 kg·m² of inertia. So damping gains around 0.15–0.25 are well damped and stable at the 8 ms control step. Gravity torque about the ankle is about 100 N·m per radian, and the ankle stiffness of 2.0 × 200 = 400 N·m per radian is well above that.
- **Starting drop:** at reset the foot starts about 4 cm above the ground. The damping absorbs the small drop.

```python
import numpy as np

# Joint-space gains (action units; actuator gear is 200 N*m per unit)
HIP_KP, HIP_KD = 1.5, 0.15      # torso-upright loop on the hip
KNEE_KP, KNEE_KD = 2.0, 0.2     # keep knee straight
ANK_KP, ANK_KD = 2.0, 0.25      # keep leg perpendicular to foot
ANK_KV = 0.2                    # push back against forward drift


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q_leg, q_foot = o[3], o[4]
    xvel = o[5]
    torso_w = o[7]
    dq_leg, dq_foot = o[9], o[10]

    # Hip torque acts +tau on thigh, -tau on torso: positive torso tilt -> positive tau.
    a_hip = HIP_KP * torso_ang + HIP_KD * torso_w

    a_knee = -KNEE_KP * q_leg - KNEE_KD * dq_leg

    a_ankle = -ANK_KP * q_foot - ANK_KD * dq_foot - ANK_KV * xvel

    a = np.clip([a_hip, a_knee, a_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```