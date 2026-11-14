import numpy as np

_K = np.array([0.3, 4.0, 0.5, 0.7])


def reset():
    pass


def act(obs):
    a = float(np.dot(_K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, a))]
