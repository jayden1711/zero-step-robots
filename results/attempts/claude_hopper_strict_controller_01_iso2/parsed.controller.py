import numpy as np

def reset():
    pass

def act(obs):
    ang = obs[1]
    w = obs[7]
    vx = obs[5]
    leg_ang = obs[3]
    leg_w = obs[9]

    foot = 6.0 * ang + 0.6 * w + 0.15 * vx
    thigh = 2.5 * ang + 0.3 * w + 0.1 * vx
    leg = -1.0 * leg_ang - 0.05 * leg_w

    a = np.clip([thigh, leg, foot], -1.0, 1.0)
    return [float(x) for x in a]
