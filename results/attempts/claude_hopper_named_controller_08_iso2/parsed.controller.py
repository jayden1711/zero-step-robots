import numpy as np


def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, d1, d2, d3 = obs
    a1 = -(1.5 * q1 + 0.10 * d1) + 0.5 * th + 0.05 * w
    a2 = -(1.5 * q2 + 0.10 * d2)
    a3 = 2.0 * th + 0.2 * w + 0.1 * vx - 0.3 * q3 - 0.02 * d3
    return [float(np.clip(a, -1, 1)) for a in (a1, a2, a3)]
