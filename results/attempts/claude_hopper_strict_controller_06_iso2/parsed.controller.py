import numpy as np

def reset():
    pass

def act(obs):
    z, ang, q1, q2, q3 = obs[0], obs[1], obs[2], obs[3], obs[4]
    vx, vz, wang, d1, d2, d3 = obs[5], obs[6], obs[7], obs[8], obs[9], obs[10]

    a1 = -6.0 * q1 - 0.3 * d1 + 0.2
    a2 = -6.0 * q2 - 0.3 * d2 + 0.2
    a3 = 8.0 * ang + 1.0 * wang + 0.3 * vx - 1.0 * q3 - 0.05 * d3

    return [float(np.clip(a1, -1, 1)), float(np.clip(a2, -1, 1)), float(np.clip(a3, -1, 1))]
