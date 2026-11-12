import numpy as np

KP = np.array([1.5, 1.5, 1.5])
KD = np.array([0.1, 0.1, 0.1])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    rooty = o[1]
    rooty_d = o[7]
    vx = o[5]

    a = -KP * q - KD * qd
    # hip: push torso back toward upright (reaction torque on torso)
    a[0] += 1.0 * rooty + 0.1 * rooty_d
    # ankle: mild correction of whole-body drift over the foot
    a[2] += -0.05 * vx
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
