import numpy as np

# State feedback u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement (all closed-loop poles near -5) on the
# linearised cart-pole model.
K = np.array([3.0, 9.76, 2.40, 1.90])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
