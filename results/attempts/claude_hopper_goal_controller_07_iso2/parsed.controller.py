import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q_th, q_leg = obs[2], obs[3]
    w = obs[7]
    qd_th, qd_leg = obs[8], obs[9]

    a_th = 0.1 - 5.0 * q_th - 0.3 * qd_th
    a_leg = 0.1 - 5.0 * q_leg - 0.3 * qd_leg
    a_ft = 5.0 * ang + 0.5 * w - 0.3 * obs[5]

    return [float(np.clip(a_th, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_ft, -1, 1))]
