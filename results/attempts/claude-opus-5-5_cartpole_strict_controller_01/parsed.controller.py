import numpy as np

K_X = 0.2      # cart position
K_TH = 4.5     # pole angle
K_V = 0.4      # cart velocity
K_W = 0.56     # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    a = K_X * x + K_TH * th + K_V * v + K_W * w
    if not np.isfinite(a):
        a = 0.0
    return [float(np.clip(a, -3.0, 3.0))]
