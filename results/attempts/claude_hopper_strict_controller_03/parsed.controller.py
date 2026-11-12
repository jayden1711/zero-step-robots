import numpy as np


def reset():
    pass


def act(obs):
    th = obs[1]
    q_hip, q_knee, q_ank = obs[2], obs[3], obs[4]
    vx = obs[5]
    w = obs[7]
    dq_hip, dq_knee, dq_ank = obs[8], obs[9], obs[10]

    a_hip = -(0.5 * q_hip + 0.05 * dq_hip) - (0.5 * th + 0.1 * w)
    a_knee = -(0.5 * q_knee + 0.05 * dq_knee)
    a_ank = -(1.5 * th + 0.2 * w + 0.1 * vx) - (0.2 * q_ank + 0.02 * dq_ank)

    a = np.clip([a_hip, a_knee, a_ank], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
