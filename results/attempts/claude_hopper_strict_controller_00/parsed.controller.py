import numpy as np


def reset():
    pass


def act(obs):
    ang = obs[1]
    thigh, leg, foot = obs[2], obs[3], obs[4]
    vx = obs[5]
    w = obs[7]
    dthigh, dleg, dfoot = obs[8], obs[9], obs[10]

    # Hold thigh and leg extended against gravity (upper joint limit is 0).
    a_thigh = 0.4 - 1.0 * thigh - 0.05 * dthigh
    a_leg = 0.4 - 1.0 * leg - 0.05 * dleg

    # Ankle strategy: push toe down when leaning forward.
    a_foot = 5.0 * ang + 0.5 * w + 0.2 * vx - 0.1 * foot - 0.02 * dfoot

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
