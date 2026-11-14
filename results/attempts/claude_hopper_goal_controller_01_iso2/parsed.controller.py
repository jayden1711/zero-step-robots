import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    angvel = obs[7]
    foot = 2.0 * ang + 0.4 * angvel + 0.3 * obs[5] * 0.0
    thigh = -1.0 * obs[2] - 0.1 * obs[8]
    leg = -1.0 * obs[3] - 0.1 * obs[9]
    a = np.clip([thigh, leg, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
