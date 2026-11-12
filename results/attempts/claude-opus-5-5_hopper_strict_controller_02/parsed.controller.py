import numpy as np

# PD posture hold: keep thigh, leg and foot joints at fixed targets so the
# body stands as a rigid, statically stable stack on the flat foot.
KP = np.array([2.0, 2.0, 2.0])      # action units per rad (x200 Nm via gear)
KD = np.array([0.2, 0.2, 0.2])      # action units per rad/s
TARGET = np.array([0.0, 0.0, 0.0])  # thigh, leg, foot joint angles (rad)


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    a = KP * (TARGET - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
