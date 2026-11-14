import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q_thigh, q_leg, q_foot, vx, vz, w, w_thigh, w_leg, w_foot = obs

    vx_c = max(-1.0, min(1.0, vx))
    target = -0.03 - 0.02 * max(0.0, 1.0 - vx_c)
    err = ang - target

    foot = 6.0 * err + 0.8 * w
    thigh = 3.0 * err + 0.4 * w - 0.5 * q_thigh - 0.05 * w_thigh
    leg = -3.0 * q_leg - 0.3 * w_leg

    return [float(np.clip(thigh, -1, 1)),
            float(np.clip(leg, -1, 1)),
            float(np.clip(foot, -1, 1))]
