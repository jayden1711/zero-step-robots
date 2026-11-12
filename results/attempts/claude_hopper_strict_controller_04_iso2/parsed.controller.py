import numpy as np


def reset():
    pass


def act(obs):
    theta = obs[1]
    q = obs[2:5]
    w = obs[7]
    qd = obs[8:11]

    a = -2.0 * np.array(q) - 0.1 * np.array(qd)
    a[2] += 1.5 * theta + 0.3 * w
    a[0] += 1.0 * theta + 0.15 * w
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
