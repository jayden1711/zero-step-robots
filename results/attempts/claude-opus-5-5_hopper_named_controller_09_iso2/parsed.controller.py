import numpy as np

KP = np.array([1.5, 1.5, 1.5])
KD = np.array([0.15, 0.15, 0.15])
TARGET = np.array([0.0, 0.0, 0.0])

# torso-angle stabilisation through the hip
K_TORSO = 1.0
KD_TORSO = 0.1


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q = o[2:5]
    dq = o[8:11]
    torso_w = o[7]

    a = KP * (TARGET - q) - KD * dq

    # hip torque reaction on the torso pushes torso angle back toward zero
    a[0] += K_TORSO * torso_ang + KD_TORSO * torso_w

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
