import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q1, q2, q3, vx, vz, w, w1, w2, w3 = [float(v) for v in obs]

    a1 = -3.0 * q1 - 0.2 * w1
    a2 = -3.0 * q2 - 0.2 * w2
    a3 = 1.5 * ang + 0.25 * w - 0.5 * q3 - 0.05 * w3

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
