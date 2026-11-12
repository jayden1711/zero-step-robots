import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    w = obs[7]
    q_t, q_l, q_f = obs[2], obs[3], obs[4]
    dq_t, dq_l, dq_f = obs[8], obs[9], obs[10]

    foot = 4.0 * ang + 0.4 * w - 0.3 * q_f - 0.02 * dq_f
    thigh = 1.5 * ang + 0.15 * w - 1.0 * q_t - 0.05 * dq_t
    leg = -1.0 * q_l - 0.05 * dq_l

    a = np.clip([thigh, leg, foot], -1.0, 1.0)
    return [float(x) for x in a]
