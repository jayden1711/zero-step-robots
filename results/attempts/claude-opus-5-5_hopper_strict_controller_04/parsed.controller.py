import numpy as np

# Joint PD gains (thigh, leg, foot)
KP = np.array([2.0, 2.0, 1.5])
KD = np.array([0.2, 0.2, 0.15])

# Small torso-pitch corrections
K_HIP_PITCH = 1.0
K_HIP_PITCH_D = 0.1
K_ANKLE_PITCH = 0.5
K_ANKLE_PITCH_D = 0.05


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    q = o[2:5]
    pitch_rate = o[7]
    qd = o[8:11]

    a = -KP * q - KD * qd

    # Hip: push the torso back toward upright (negative thigh torque reduces pitch)
    a[0] += -K_HIP_PITCH * pitch - K_HIP_PITCH_D * pitch_rate
    # Ankle: lean the body back over the foot if it tips
    a[2] += -K_ANKLE_PITCH * pitch - K_ANKLE_PITCH_D * pitch_rate

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
