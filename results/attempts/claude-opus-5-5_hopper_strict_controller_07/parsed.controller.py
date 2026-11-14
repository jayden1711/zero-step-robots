import numpy as np

# Joint PD gains (action units per rad and per rad/s; torque = 200 * action)
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.10, 0.10, 0.10])
TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    a = KP * (TARGET - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
