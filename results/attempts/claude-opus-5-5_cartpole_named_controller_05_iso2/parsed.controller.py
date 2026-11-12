import numpy as np

# Linear state feedback u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement (poles at -4, -4, -6, -6) on a linearised
# model of the MuJoCo InvertedPendulum (gear 100).
K = np.array([1.567, 5.58, 1.305, 1.053])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
