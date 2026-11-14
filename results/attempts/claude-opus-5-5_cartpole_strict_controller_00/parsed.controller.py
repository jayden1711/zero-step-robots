import numpy as np

K_X = 0.2      # cart position
K_TH = 8.0     # pole angle
K_V = 0.4      # cart velocity
K_W = 1.2      # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    u = K_X * x + K_TH * th + K_V * v + K_W * w
    if not np.isfinite(u):
        u = 0.0
    return [float(np.clip(u, -3.0, 3.0))]
