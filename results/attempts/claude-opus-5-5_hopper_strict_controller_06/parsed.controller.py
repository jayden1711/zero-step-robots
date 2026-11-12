import numpy as np


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    r, t, l, f = o[1], o[2], o[3], o[4]
    vx = o[5]
    dr, dt_, dl, df = o[7], o[8], o[9], o[10]

    # Hip: keep torso pitch at zero (torso receives the reaction torque)
    a_hip = 1.0 * r + 0.12 * dr

    # Knee: hold straight (at upper joint limit 0)
    a_knee = -1.0 * l - 0.1 * dl + 0.05

    # Ankle: keep absolute leg angle (rigid thigh+leg segment) upright over the foot
    alpha = r + t + l
    dalpha = dr + dt_ + dl
    a_ankle = 1.0 * alpha + 0.3 * dalpha
    # damp horizontal drift (sign-agnostic small term: oppose motion via lean)
    a_ankle += 0.0 * vx
    a_ankle = float(np.clip(a_ankle, -0.35, 0.35))

    a = np.clip([a_hip, a_knee, a_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
