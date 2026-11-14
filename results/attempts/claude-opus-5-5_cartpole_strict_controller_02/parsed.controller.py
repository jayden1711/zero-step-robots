import numpy as np

# Linear state feedback: u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement (poles at -1.5, -1.5, -6, -6) on a linearised cart-pole model.
K = np.array([0.389, 5.16, 0.648, 0.963])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
