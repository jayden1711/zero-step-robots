import numpy as np

# Posture targets
LEG_LEAN_TARGET = -0.05   # absolute leg angle (slightly forward, CoM over mid-foot)
TORSO_TARGET = 0.0
KNEE_TARGET = 0.0

# Gains (action units; gear ~200)
KT, DT = 1.0, 0.1     # torso via hip
KK, DK = 2.0, 0.2     # knee
KA, DA = 1.5, 0.3     # ankle balance


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q1, q2, q3, q4 = o[1], o[2], o[3], o[4]
    w1, w2, w3, w4 = o[7], o[8], o[9], o[10]

    # Hip: keep torso upright (positive hip torque pitches torso forward)
    u_hip = KT * (q1 - TORSO_TARGET) + DT * w1

    # Knee: hold straight
    u_knee = -KK * (q3 - KNEE_TARGET) - DK * w3

    # Ankle: inverted-pendulum balance on absolute leg angle
    phi = q1 + q2 + q3
    phid = w1 + w2 + w3
    u_ankle = KA * (phi - LEG_LEAN_TARGET) + DA * phid

    a = np.clip([u_hip, u_knee, u_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
