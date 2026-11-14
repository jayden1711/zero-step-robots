import numpy as np

KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.3, 0.3, 0.3])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]

    # PD hold every joint at zero (straight, upright leg, flat foot)
    a = -KP * q - KD * qd

    # Small torso-upright correction through the hip
    pitch = o[1]
    pitch_rate = o[7]
    a[0] += 0.5 * pitch + 0.05 * pitch_rate

    return [float(x) for x in np.clip(a, -1.0, 1.0)]
