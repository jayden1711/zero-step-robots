import numpy as np

# Linear state feedback: u = K . [x, theta, v, omega]
# Gains from pole placement at {-3, -3, -8, -8} on the linearised cart-pole model.
K = np.array([2.77, 10.56, 2.54, 2.05])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
