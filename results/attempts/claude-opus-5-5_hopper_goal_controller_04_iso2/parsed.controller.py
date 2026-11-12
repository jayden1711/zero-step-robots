import numpy as np

# Joint-space PD gains (action units per rad, per rad/s)
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.12, 0.12, 0.10])

# Extra torso-pitch feedback applied through the ankle
K_PITCH = 1.0
D_PITCH = 0.08


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    pitch = obs[1]
    q = obs[2:5]
    pitch_rate = obs[7]
    qd = obs[8:11]

    # Hold a rigid, straight posture
    a = -KP * q - KD * qd

    # Ankle balance: if torso leans forward (pitch > 0), press toe down,
    # which rotates the body back over the foot (and vice versa)
    a[2] += K_PITCH * pitch + D_PITCH * pitch_rate

    # Keep the upper joints from letting the torso drift
    a[0] += 0.5 * pitch + 0.05 * pitch_rate

    return [float(x) for x in np.clip(a, -1.0, 1.0)]
