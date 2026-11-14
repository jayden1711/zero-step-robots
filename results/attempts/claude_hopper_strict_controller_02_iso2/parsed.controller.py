import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q_thigh, q_leg, q_foot = obs[2], obs[3], obs[4]
    w = obs[7]
    dthigh, dleg, dfoot = obs[8], obs[9], obs[10]

    a_foot = 3.0 * ang + 0.3 * w - 0.5 * q_foot - 0.02 * dfoot
    a_thigh = 1.0 * ang + 0.1 * w - 1.0 * q_thigh - 0.05 * dthigh
    a_leg = -2.0 * q_leg - 0.1 * dleg

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
