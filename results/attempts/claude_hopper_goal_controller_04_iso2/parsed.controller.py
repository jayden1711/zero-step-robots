import numpy as np


def reset():
    pass


def act(obs):
    z, ang = obs[0], obs[1]
    q_thigh, q_leg, q_foot = obs[2], obs[3], obs[4]
    vx, vz, wang = obs[5], obs[6], obs[7]
    dq_thigh, dq_leg, dq_foot = obs[8], obs[9], obs[10]

    # Ankle: resist torso lean and forward drift
    foot = 3.0 * ang + 0.4 * wang + 0.2 * vx - 0.3 * q_foot - 0.02 * dq_foot
    # Hip: help level the torso while holding the thigh near neutral
    thigh = 1.0 * ang + 0.2 * wang - 0.5 * q_thigh - 0.03 * dq_thigh
    # Knee: hold the leg near straight
    leg = -1.0 * q_leg - 0.05 * dq_leg

    return [float(np.clip(thigh, -1, 1)),
            float(np.clip(leg, -1, 1)),
            float(np.clip(foot, -1, 1))]
