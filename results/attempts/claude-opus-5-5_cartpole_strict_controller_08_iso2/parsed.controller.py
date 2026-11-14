import numpy as np

# Linear state feedback: a = K . [x, theta, xdot, thetadot]
# Gains from pole placement (all closed-loop poles at s = -4) on a linearised cart-pole model.
K = np.array([1.23, 6.52, 1.23, 1.24])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    a = float(np.dot(K, s))
    a = max(-3.0, min(3.0, a))
    return [a]
