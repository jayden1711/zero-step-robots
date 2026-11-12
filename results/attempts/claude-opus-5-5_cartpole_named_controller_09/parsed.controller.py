import numpy as np

# State feedback gains: u = K . [x, theta, x_dot, theta_dot]
# Pole terms stabilise the pendulum; small cart terms keep the cart centred.
K_X = 0.08
K_TH = 3.8
K_V = 0.2
K_W = 0.6


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    if not all(np.isfinite([x, th, v, w])):
        return [0.0]
    u = K_X * x + K_TH * th + K_V * v + K_W * w
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
