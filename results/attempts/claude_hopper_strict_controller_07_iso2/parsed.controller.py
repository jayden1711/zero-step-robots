import numpy as np

def reset():
    pass

def act(obs):
    th = obs[1]
    w = obs[7]
    q2, q3 = obs[2], obs[3]
    d2, d3 = obs[9], obs[10]
    foot = 4.0 * th + 0.6 * w
    thigh = -2.0 * q2 - 0.1 * d2
    knee = -2.0 * q3 - 0.1 * d3
    a = np.clip([thigh, knee, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
