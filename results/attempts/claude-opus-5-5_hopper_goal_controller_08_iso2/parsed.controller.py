import numpy as np

# Target lean (rad) of the rigid leg+torso stick about the ankle; slightly
# forward so the centre of mass sits over the middle of the foot.
PHI_TARGET = 0.04

KP_ANKLE = 1.5
KD_ANKLE = 0.35
ANKLE_LIM = 0.2

KP_JOINT = 3.0
KD_JOINT = 0.15
JOINT_BIAS = 0.15   # press hip/knee into their straight (0) limit


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    theta, q_thigh, q_leg, q_foot = obs[1], obs[2], obs[3], obs[4]
    dtheta, dq_thigh, dq_leg = obs[7], obs[8], obs[9]

    # Hip and knee: hold straight, biased into the joint limit.
    a_hip = KP_JOINT * (0.0 - q_thigh) - KD_JOINT * dq_thigh + JOINT_BIAS
    a_knee = KP_JOINT * (0.0 - q_leg) - KD_JOINT * dq_leg + JOINT_BIAS

    # Ankle: balance the stick as an inverted pendulum.
    phi = theta - q_thigh - q_leg
    dphi = dtheta - dq_thigh - dq_leg
    a_foot = -KP_ANKLE * (phi - PHI_TARGET) - KD_ANKLE * dphi
    a_foot = float(np.clip(a_foot, -ANKLE_LIM, ANKLE_LIM))

    a = np.clip([a_hip, a_knee, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
