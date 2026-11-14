import numpy as np

K_THETA = 5.0
K_OMEGA = 0.6
K_X = 0.1
K_V = 0.2


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    u = K_THETA * th + K_OMEGA * w + K_X * x + K_V * v
    if not np.isfinite(u):
        u = 0.0
    return [float(np.clip(u, -3.0, 3.0))]
