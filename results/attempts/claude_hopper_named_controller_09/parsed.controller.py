import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    q_thigh, q_leg = obs[2], obs[3]
    w = obs[7]
    w_thigh, w_leg = obs[8], obs[9]

    # Thigh and leg joints have an upper limit at 0; push against it to keep the leg straight.
    a_thigh = -3.0 * q_thigh - 0.1 * w_thigh
    a_leg = -3.0 * q_leg - 0.1 * w_leg

    # Forward lean (positive angle) is countered by positive ankle torque.
    a_foot = 2.0 * ang + 0.5 * w

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_foot, -1, 1))]
