import numpy as np


def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, dq1, dq2, dq3 = [float(v) for v in obs]

    a1 = 0.3 - 3.0 * q1 - 0.1 * dq1
    a2 = 0.3 - 3.0 * q2 - 0.1 * dq2

    a3 = 1.5 * th + 0.3 * w - 0.5 * q3 - 0.02 * dq3

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
