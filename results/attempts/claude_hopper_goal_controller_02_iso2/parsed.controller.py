import numpy as np

def reset():
    pass

def act(obs):
    ang = obs[1]
    q_thigh, q_leg = obs[2], obs[3]
    w_ang = obs[7]
    w_thigh, w_leg = obs[8], obs[9]

    a0 = -2.0 * q_thigh - 0.05 * w_thigh
    a1 = -2.0 * q_leg - 0.05 * w_leg
    a2 = -4.0 * ang - 0.4 * w_ang

    return [float(np.clip(a0, -1, 1)), float(np.clip(a1, -1, 1)), float(np.clip(a2, -1, 1))]
