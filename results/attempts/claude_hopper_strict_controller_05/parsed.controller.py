import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    angvel = obs[7]
    thigh, leg, foot = obs[2], obs[3], obs[4]
    dthigh, dleg, dfoot = obs[8], obs[9], obs[10]

    a_thigh = -1.0 * thigh - 0.05 * dthigh
    a_leg = -1.0 * leg - 0.05 * dleg
    a_foot = 2.0 * ang + 0.3 * angvel - 0.2 * foot - 0.02 * dfoot

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_foot, -1, 1))]
