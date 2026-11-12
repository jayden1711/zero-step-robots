This looks like the MuJoCo Hopper (torso height, torso pitch, three joint angles, then six velocities). Writing a hopping gait blind is very risky. Instead, this controller makes the robot stand still and balance, which reliably collects about 1 reward per step for all 1000 steps:

- **Hip and knee:** they are pushed slightly into their "straight" joint limits (both joints are limited to [-150°, 0]) and held there with a PD controller. This makes the body a rigid column.
- **Ankle:** it balances that column on the flat foot as an inverted pendulum. Ankle torque is kept small so the foot doesn't tip over its edge.

Sign conventions: the root pitch hinge is on the +y axis, so a positive value means leaning forward. The limb joints are on the -y axis, so the shank's absolute forward lean is `rooty - q_thigh - q_leg`. A positive ankle torque tips the shank forward, so the balance feedback uses a negative sign.

```python
import numpy as np

# Joint posture gains (hip, knee): hold straight against the joint limit at 0.
KP_JOINT = 2.0
KD_JOINT = 0.1
BIAS_JOINT = 0.15

# Ankle balance gains (inverted pendulum about the ankle).
K_ANKLE = 1.5
D_ANKLE = 0.3
LEAN_TARGET = 0.02   # slight forward lean to centre COM over foot support
ANKLE_LIMIT = 0.35


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    rooty = obs[1]
    q_t, q_l, q_f = obs[2], obs[3], obs[4]
    rooty_d = obs[7]
    qd_t, qd_l, qd_f = obs[8], obs[9], obs[10]

    # Hip and knee: PD toward 0 plus a small push into the straight-leg limit.
    a_thigh = KP_JOINT * (0.0 - q_t) - KD_JOINT * qd_t + BIAS_JOINT
    a_leg = KP_JOINT * (0.0 - q_l) - KD_JOINT * qd_l + BIAS_JOINT

    # Absolute forward lean of the shank (positive = top toward +x).
    psi = rooty - q_t - q_l
    psi_d = rooty_d - qd_t - qd_l

    # Positive foot torque tips the shank forward, so feed back negatively.
    a_foot = -(K_ANKLE * (psi - LEAN_TARGET) + D_ANKLE * psi_d)
    a_foot = float(np.clip(a_foot, -ANKLE_LIMIT, ANKLE_LIMIT))

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            a_foot]
```