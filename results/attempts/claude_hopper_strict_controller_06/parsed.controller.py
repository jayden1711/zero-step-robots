import numpy as np


def reset():
    pass


def act(obs):
    z, ang, th, lg, ft = obs[0], obs[1], obs[2], obs[3], obs[4]
    vx, vz, wang, wth, wlg, wft = obs[5], obs[6], obs[7], obs[8], obs[9], obs[10]

    a_foot = 2.5 * ang + 0.25 * wang - 0.05 * wft
    a_thigh = -1.0 * th - 0.1 * wth
    a_leg = -1.0 * lg - 0.1 * wlg

    # small damping of forward drift keeps balance; mild lean for speed
    a_foot += 0.15 * vx

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
