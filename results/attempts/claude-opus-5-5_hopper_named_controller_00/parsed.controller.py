import numpy as np

# Joint-space PD gains (action units; actuator gear is 200)
KP = np.array([3.0, 3.0, 2.5])
KD = np.array([0.25, 0.25, 0.2])

# Small whole-body tilt correction, kept weak and saturated for robustness
K_TILT = 0.5
K_TILT_RATE = 0.05
TILT_LIMIT = 0.15


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q = o[2:5]
    torso_w = o[7]
    qd = o[8:11]

    # Hold all joints straight (rigid stance over the foot)
    a = -KP * q - KD * qd

    # Gentle tilt correction via the thigh joint: rotate the torso back toward
    # upright relative to the leg; saturated so it cannot dominate the stance.
    tilt = float(np.clip(K_TILT * torso_ang + K_TILT_RATE * torso_w,
                         -TILT_LIMIT, TILT_LIMIT))
    a[0] += tilt

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
