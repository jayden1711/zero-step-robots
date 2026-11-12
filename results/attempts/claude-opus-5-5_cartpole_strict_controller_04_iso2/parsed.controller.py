import numpy as np

K_X = 0.25      # cart position
K_TH = 4.5      # pole angle
K_V = 0.5       # cart velocity
K_W = 0.6       # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    if not all(np.isfinite([x, th, v, w])):
        return [0.0]
    u = K_X * x + K_TH * th + K_V * v + K_W * w
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
