import numpy as np

def reset():
    pass

def act(obs):
    x, th, xd, thd = [float(v) for v in obs]
    u = 0.1 * x + 4.0 * th + 0.4 * xd + 0.6 * thd
    return [float(np.clip(u, -3.0, 3.0))]
