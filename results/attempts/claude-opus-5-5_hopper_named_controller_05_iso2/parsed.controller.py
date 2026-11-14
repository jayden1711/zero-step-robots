import numpy as np

KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.25, 0.25, 0.25])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q = o[2:5]
    torso_angvel = o[7]
    qd = o[8:11]

    a = -KP * q - KD * qd

    # Hip: keep the torso upright relative to the world.
    a[0] += -1.5 * torso_ang - 0.1 * torso_angvel
    # Ankle strategy: counter whole-body tilt via torque against the ground.
    a[2] += 1.0 * torso_ang + 0.1 * torso_angvel

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
