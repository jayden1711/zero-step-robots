import numpy as np

KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.12, 0.12, 0.12])


def reset():
    pass


def act(obs):
    q = np.array(obs[2:5], dtype=float)
    qd = np.array(obs[8:11], dtype=float)
    a = -KP * q - KD * qd
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
