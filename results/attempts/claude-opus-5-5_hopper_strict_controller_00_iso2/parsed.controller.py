import numpy as np

_integ = 0.0


def reset():
    global _integ
    _integ = 0.0


def act(obs):
    global _integ
    o = np.asarray(obs, dtype=float)
    th, qt, qk, qf = o[1], o[2], o[3], o[4]
    thd, qtd, qkd, qfd = o[7], o[8], o[9], o[10]

    # Hip: keep torso upright (reaction torque on torso is +u about +y)
    u_hip = -1.5 * th - 0.1 * thd

    # Knee: keep straight
    u_knee = 2.0 * (0.0 - qk) - 0.1 * qkd + 0.05

    # Ankle: keep leg lean over foot near small forward target
    phi = th - qt - qk
    phid = thd - qtd - qkd
    err = phi - 0.02
    _integ = float(np.clip(_integ + err * 0.008, -0.2, 0.2))
    u_ank = -0.8 * err - 0.15 * phid - 0.3 * _integ
    u_ank = float(np.clip(u_ank, -0.1, 0.1))

    return [float(np.clip(u_hip, -1, 1)),
            float(np.clip(u_knee, -1, 1)),
            u_ank]
