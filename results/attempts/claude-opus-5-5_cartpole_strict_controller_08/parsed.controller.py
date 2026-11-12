import numpy as np

# Linear state feedback: u = K . [x, theta, x_dot, theta_dot]
# Gains chosen by pole placement on a linearised cart-pole model and checked
# (Routh-Hurwitz) to remain stable across a wide range of mass/inertia guesses.
K = np.array([2.0, 7.5, 1.8, 1.4])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if s.shape[0] < 4 or not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s[:4]))
    u = max(-3.0, min(3.0, u))
    return [u]
