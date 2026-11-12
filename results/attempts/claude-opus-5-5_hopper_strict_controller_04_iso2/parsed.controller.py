import numpy as np

# Observation layout (Hopper-like):
# 0 z, 1 torso pitch, 2 thigh, 3 leg, 4 foot,
# 5 xvel, 6 zvel, 7 pitch rate, 8 thigh vel, 9 leg vel, 10 foot vel

KP = np.array([1.5, 1.5, 1.5])
KD = np.array([0.08, 0.08, 0.15])
TARGET = np.array([0.0, 0.0, 0.0])

# Torso-upright feedback distributed to hip and ankle
K_PITCH = np.array([0.5, 0.0, 0.8])
K_PITCH_RATE = np.array([0.03, 0.0, 0.05])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    pitch = o[1]
    pitch_rate = o[7]

    a = KP * (TARGET - q) - KD * qd
    # If the torso pitches forward (positive), rotate joints to bring it back.
    a -= K_PITCH * pitch + K_PITCH_RATE * pitch_rate

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
