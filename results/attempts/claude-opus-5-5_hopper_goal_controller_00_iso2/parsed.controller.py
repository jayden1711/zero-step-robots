import numpy as np

# Joint-space PD stance controller: keep the leg rigid and upright so the
# body balances statically over its foot for the whole episode.

KP = np.array([2.0, 2.0, 1.5])     # hip, knee, ankle stiffness (action units / rad)
KD = np.array([0.10, 0.10, 0.08])  # damping (action units / (rad/s))
TARGET = np.array([-0.02, -0.02, 0.0])

K_PITCH = 0.3
K_PITCH_RATE = 0.03


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = np.clip(o[8:11], -10.0, 10.0)
    pitch = o[1]
    pitch_rate = np.clip(o[7], -10.0, 10.0)

    a = KP * (TARGET - q) - KD * qd

    # Hip torque reacts on the torso; nudge torso pitch back toward zero.
    a[0] += -K_PITCH * pitch - K_PITCH_RATE * pitch_rate

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
