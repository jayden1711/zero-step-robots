import numpy as np

# Linear state feedback: u = K . [x, theta, x_dot, theta_dot]
# Derived by pole placement (all poles at -4 rad/s) on the linearised cart-pole
# model of InvertedPendulum (cart ~10.5 kg, pole ~5 kg, gear 100).
K = np.array([1.228, 6.52, 1.228, 1.243])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
