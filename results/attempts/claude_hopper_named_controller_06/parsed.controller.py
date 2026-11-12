import numpy as np


def reset():
    pass


def act(obs):
    q_thigh, q_leg = obs[2], obs[3]
    ang, angvel = obs[1], obs[7]
    qd_thigh, qd_leg = obs[8], obs[9]

    a_thigh = 0.3 - 5.0 * q_thigh - 0.05 * qd_thigh
    a_leg = 0.3 - 5.0 * q_leg - 0.05 * qd_leg
    a_foot = 4.0 * ang + 0.5 * angvel

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_foot, -1, 1))]
