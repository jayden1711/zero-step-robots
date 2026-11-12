import numpy as np

# Linear state feedback for a cart-pole: obs = [x, theta, x_dot, theta_dot]
K_X = 0.1
K_THETA = 5.5
K_XDOT = 0.25
K_THETADOT = 0.9


def reset():
    pass


def act(obs):
    x, theta, xdot, thetadot = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, theta, xdot, thetadot])):
        return [0.0]
    u = K_X * x + K_THETA * theta + K_XDOT * xdot + K_THETADOT * thetadot
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
