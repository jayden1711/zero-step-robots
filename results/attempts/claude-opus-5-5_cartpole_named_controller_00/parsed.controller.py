import numpy as np

# Gains from pole placement at (s+1.5)^2 (s+4)^2 on the linearised cart-pole:
#   x_dd  ~ 15 u - 5.4 theta
#   th_dd ~ 38 theta - 37.5 u
K_X = 0.098      # cart position
K_V = 0.18       # cart velocity
K_TH = 2.18      # pole angle
K_W = 0.365      # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    if not all(np.isfinite([x, th, v, w])):
        return [0.0]
    u = K_X * x + K_V * v + K_TH * th + K_W * w
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
