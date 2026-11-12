import numpy as np

# Target joint angles: the upright initial pose (thigh, leg, foot).
Q_DES = np.array([0.0, 0.0, 0.0])

# PD gains in action units (actuator gear is 200 Nm per unit action).
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.1, 0.1, 0.1])


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    a = -KP * (q - Q_DES) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
