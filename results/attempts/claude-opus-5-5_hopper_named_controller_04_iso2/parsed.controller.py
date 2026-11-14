import numpy as np

# Joint-space PD gains (action units; actuator gear is 200)
KP = np.array([4.0, 4.0, 4.0])
KD = np.array([0.2, 0.2, 0.2])
TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    a = -KP * (q - TARGET) - KD * qd
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
