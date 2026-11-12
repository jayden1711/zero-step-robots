import numpy as np


def reset():
    pass


def act(obs):
    q0 = obs[1]      # torso pitch
    q1 = obs[2]      # hip
    q2 = obs[3]      # knee
    w0 = obs[7]      # pitch rate
    w1 = obs[8]
    w2 = obs[9]

    a3 = 5.0 * q0 + 0.5 * w0
    a1 = -2.0 * q1 - 0.1 * w1
    a2 = -2.0 * q2 - 0.1 * w2

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
