import numpy as np

def reset():
    pass

def act(obs):
    th = obs[1]
    q_hip, q_knee, q_ank = obs[2], obs[3], obs[4]
    w = obs[7]
    vx = obs[5]
    qd_hip, qd_knee, qd_ank = obs[8], obs[9], obs[10]

    lean = 4.0 * th + 0.5 * w + 0.15 * vx

    a_hip = lean - 1.0 * q_hip - 0.05 * qd_hip
    a_knee = -1.5 * q_knee - 0.05 * qd_knee
    a_ank = lean - 0.5 * q_ank - 0.03 * qd_ank

    return [float(np.clip(a_hip, -1, 1)),
            float(np.clip(a_knee, -1, 1)),
            float(np.clip(a_ank, -1, 1))]
