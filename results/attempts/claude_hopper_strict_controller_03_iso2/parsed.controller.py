import numpy as np

def reset():
    pass

def act(obs):
    th = obs[1]
    q1, q2, q3 = obs[2], obs[3], obs[4]
    w = obs[7]
    d1, d2, d3 = obs[8], obs[9], obs[10]

    foot = 3.0 * th + 0.4 * w - 0.3 * q3 - 0.05 * d3
    hip = 2.0 * th + 0.3 * w - 0.5 * q1 - 0.05 * d1
    leg = -1.0 * q2 - 0.1 * d2

    a = np.clip([hip, leg, foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
