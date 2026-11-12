import numpy as np

# Joint PD gains (action units; actuator gear ~200 Nm per unit)
KP = np.array([1.0, 1.0, 0.8])
KD = np.array([0.05, 0.05, 0.04])
# Joint targets: straight posture
Q_TARGET = np.array([0.0, 0.0, 0.0])

# Torso uprightness correction through the hip
K_TORSO_P = 1.0
K_TORSO_D = 0.05
# Whole-body balance correction through the ankle
K_ANKLE_P = 0.5
K_ANKLE_D = 0.03


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    q = o[2:5]
    pitch_rate = o[7]
    qd = o[8:11]

    u = -KP * (q - Q_TARGET) - KD * qd

    # Hip: torque on the thigh joint reacts on the torso with opposite sign;
    # torso leaning back (pitch > 0) -> positive hip torque rotates torso forward.
    u[0] += K_TORSO_P * pitch + K_TORSO_D * pitch_rate

    # Ankle: keep overall body lean centred over the foot.
    u[2] += K_ANKLE_P * pitch + K_ANKLE_D * pitch_rate

    u = np.clip(u, -1.0, 1.0)
    return [float(u[0]), float(u[1]), float(u[2])]
