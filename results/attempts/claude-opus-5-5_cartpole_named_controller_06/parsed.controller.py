import numpy as np

# Linear state feedback u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement on a linearised cart-pole model of
# InvertedPendulum-v5 (cart ~10.5 kg, pole ~5 kg, gear 100):
#   pole dynamics: double pole at -6 rad/s
#   cart dynamics: double pole at -1.5 rad/s
K = np.array([0.372, 4.97, 0.62, 0.924])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
