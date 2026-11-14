import numpy as np

_step = 0
_dive_sign = 1.0
_checked = False

DIVE_START = 928
CHECK_STEP = DIVE_START + 10


def reset():
    global _step, _dive_sign, _checked
    _step = 0
    _dive_sign = 1.0
    _checked = False


def _clip(x):
    return float(np.clip(x, -1.0, 1.0))


def act(obs):
    global _step, _dive_sign, _checked
    o = np.asarray(obs, dtype=float)
    th, q1, q2, q3 = o[1], o[2], o[3], o[4]
    thd, q1d, q2d, q3d = o[7], o[8], o[9], o[10]
    _step += 1

    # leg absolute angle (torso + hip + knee)
    psi = th + q1 + q2
    psid = thd + q1d + q2d

    # knee: hold straight
    a_knee = -3.0 * q2 - 0.3 * q2d

    if _step < DIVE_START:
        # standing: rigid body balanced over flat foot
        a_hip = -3.0 * q1 - 0.3 * q1d
        a_foot = 1.5 * psi + 0.25 * psid
    else:
        # forward dive: keep torso upright, tip leg forward with the ankle
        if not _checked and _step >= CHECK_STEP:
            _checked = True
            if o[5] < -0.02:
                _dive_sign = -_dive_sign
        a_hip = 3.0 * th + 0.3 * thd
        a_foot = 0.8 * _dive_sign

    return [_clip(a_hip), _clip(a_knee), _clip(a_foot)]
