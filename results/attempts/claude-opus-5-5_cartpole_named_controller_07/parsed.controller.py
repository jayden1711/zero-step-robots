import numpy as np

# Linear state feedback: u = Kx*x + Kv*v + Kth*theta + Kw*omega
# Positive pole angle leans toward +x, so all gains are positive
# (push the cart under the falling pole; position terms are the slow outer loop).
K_X = 0.3
K_V = 0.5
K_TH = 6.0
K_W = 0.8


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    u = K_X * x + K_V * v + K_TH * th + K_W * w
    if not np.isfinite(u):
        u = 0.0
    return [float(np.clip(u, -3.0, 3.0))]
