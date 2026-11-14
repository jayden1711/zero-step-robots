import numpy as np

def reset():
    pass

def act(obs):
    z, th, q1, q2, q3, vx, vz, w, w1, w2, w3 = obs
    a1 = -3.0 * q1 - 0.1 * w1
    a2 = -3.0 * q2 - 0.1 * w2
    a3 = 4.0 * th + 0.4 * w - 0.5 * q3 - 0.03 * w3
    return [float(np.clip(a1, -1, 1)), float(np.clip(a2, -1, 1)), float(np.clip(a3, -1, 1))]
