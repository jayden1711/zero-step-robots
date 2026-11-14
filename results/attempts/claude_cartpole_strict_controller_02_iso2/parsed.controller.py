import numpy as np

def act(obs):
    x, th, xd, thd = obs
    u = 0.3 * x + 8.0 * th + 0.5 * xd + 1.0 * thd
    return [float(np.clip(u, -3.0, 3.0))]
