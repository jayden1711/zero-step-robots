import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    thigh = obs[3 - 1 + 0] if False else obs[2]
    leg = obs[3]
    foot = obs[4]
    angvel = obs[7]
    thigh_v = obs[8]
    leg_v = obs[9]
    foot_v = obs[10]

    a_thigh = -2.0 * thigh - 0.1 * thigh_v + 0.3
    a_leg = -2.0 * leg - 0.1 * leg_v + 0.3
    a_foot = 3.0 * ang + 0.3 * angvel - 1.0 * foot - 0.05 * foot_v

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_foot, -1, 1))]
