import numpy as np

KP = np.array([4.0, 4.0, 4.0])
KD = np.array([0.08, 0.08, 0.08])
K_TORSO = 1.0
KD_TORSO = 0.05


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    a = -KP * q - KD * qd
    # small torso-upright correction through the hip
    a[0] += K_TORSO * o[1] + KD_TORSO * o[7]
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
