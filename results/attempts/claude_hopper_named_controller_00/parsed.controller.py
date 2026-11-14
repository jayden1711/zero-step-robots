import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q_th, q_leg, q_ft, vx, vz, w, w_th, w_leg, w_ft = obs

    a_th = 6.0 * ang + 0.6 * w - 0.5 * q_th - 0.05 * w_th
    a_leg = -3.0 * q_leg - 0.15 * w_leg
    a_ft = 3.0 * ang + 0.3 * w - 0.5 * q_ft - 0.05 * w_ft

    return [float(np.clip(a_th, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            float(np.clip(a_ft, -1, 1))]
