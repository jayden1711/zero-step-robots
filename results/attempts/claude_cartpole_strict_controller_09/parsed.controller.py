import numpy as np

_K = np.array([0.15, 6.0, 0.3, 0.8])


def reset():
    pass


def act(obs):
    u = float(np.dot(_K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
