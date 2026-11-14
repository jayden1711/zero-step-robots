import numpy as np

# State feedback gains from pole placement on the linearised cart-pole model
# (closed-loop poles at -3, -3, -8, -8).
K = np.array([2.77, 10.57, 2.54, 2.05])  # [x, theta, x_dot, theta_dot]


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
