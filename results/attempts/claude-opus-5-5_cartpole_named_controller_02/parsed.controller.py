import numpy as np


def reset():
    pass


def act(obs):
    x, theta, x_dot, theta_dot = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, theta, x_dot, theta_dot])):
        return [0.0]
    u = 0.1 * x + 3.0 * theta + 0.2 * x_dot + 0.3 * theta_dot
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
