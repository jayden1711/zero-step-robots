import numpy as np

KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.08, 0.08, 0.05])
TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    a = KP * (TARGET - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
