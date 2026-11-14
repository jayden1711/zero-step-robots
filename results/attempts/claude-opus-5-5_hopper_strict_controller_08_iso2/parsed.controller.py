import numpy as np

KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.1, 0.1, 0.08])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    pitch_rate = o[7]
    q = o[2:5]
    qd = o[8:11]

    # weak, bounded torso-upright correction applied through joint targets
    corr = float(np.clip(0.3 * pitch + 0.02 * pitch_rate, -0.05, 0.05))
    target = np.array([corr, 0.0, -corr])

    a = KP * (target - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
