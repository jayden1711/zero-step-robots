import numpy as np

# PD gains in action units (actuator torque ~ gear * action)
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.25, 0.25, 0.25])
TARGET = np.array([0.0, 0.0, 0.0])

# small extra term on the hip to keep the torso upright
K_TORSO_P = 0.5
K_TORSO_D = 0.05


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]

    a = -KP * (q - TARGET) - KD * qd

    # torso angle / angular velocity: if the torso pitches, rotate the hip so the
    # torso is pushed back toward upright (reaction torque acts on torso)
    torso = o[1]
    torso_d = o[7]
    a[0] += K_TORSO_P * torso + K_TORSO_D * torso_d

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
