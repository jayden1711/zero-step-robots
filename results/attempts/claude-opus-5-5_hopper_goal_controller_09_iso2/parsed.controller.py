import numpy as np

DT = 0.008

_step = 0
_x_est = 0.0
_x_trial_start = 0.0
_sign = 1.0
_sign_decided = False
_lean = 0.0

SETTLE = 60
TRIAL_END = 140
TRIAL_LEAN = 0.03
FULL_LEAN = 0.11


def reset():
    global _step, _x_est, _x_trial_start, _sign, _sign_decided, _lean
    _step = 0
    _x_est = 0.0
    _x_trial_start = 0.0
    _sign = 1.0
    _sign_decided = False
    _lean = 0.0


def _clip(v, lo=-1.0, hi=1.0):
    return float(max(lo, min(hi, v)))


def act(obs):
    global _step, _x_est, _x_trial_start, _sign, _sign_decided, _lean
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    q_hip, q_knee, q_ank = o[2], o[3], o[4]
    vx = o[5]
    dq_hip, dq_knee, dq_ank = o[8], o[9], o[10]

    _x_est += vx * DT

    # lean schedule (ankle target, in joint units)
    if _step < SETTLE:
        target = 0.0
        _x_trial_start = _x_est
    elif _step < TRIAL_END:
        frac = (_step - SETTLE) / float(TRIAL_END - SETTLE)
        target = _sign * TRIAL_LEAN * min(1.0, 2.0 * frac)
    else:
        if not _sign_decided:
            if _x_est - _x_trial_start < 0.0:
                _sign = -_sign
            _sign_decided = True
        frac = min(1.0, (_step - TRIAL_END) / 250.0)
        target = _sign * FULL_LEAN * frac

    # safety: back off if torso pitch gets large
    if abs(pitch) > 0.13:
        target *= max(0.0, 1.0 - (abs(pitch) - 0.13) / 0.04)
    _lean = target

    # hip and knee: press into the upper joint limit (0) to keep the leg rigid
    a_hip = _clip(3.0 * (0.1 - q_hip) - 0.3 * dq_hip)
    a_knee = _clip(3.0 * (0.1 - q_knee) - 0.3 * dq_knee)

    # ankle: PD around the lean target
    a_ank = _clip(4.0 * (_lean - q_ank) - 0.3 * dq_ank)

    _step += 1
    return [a_hip, a_knee, a_ank]
