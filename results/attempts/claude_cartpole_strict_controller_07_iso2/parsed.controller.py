import numpy as np

K = np.array([0.1, 5.0, 0.3, 0.6])


def reset():
    pass


def act(obs):
    u = float(np.dot(K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
