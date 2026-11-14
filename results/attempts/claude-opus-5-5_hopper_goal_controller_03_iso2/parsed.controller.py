import math

DT = 0.008
LMAX = 0.33          # target forward lean of the (straight) leg, rad
PR_RATIO = 0.12 / 0.33  # torso lean as fraction of leg lean
RATE = 0.0013        # lean ramp rate per step (rad)
CHECK_STEP = 100

_step = 0
_lam = 0.0
_goal = LMAX
_x_est = 0.0
_checked = False


def reset():
    global _step, _lam, _goal, _x_est, _checked
    _step = 0
    _lam = 0.0
    _goal = LMAX
    _x_est = 0.0
    _checked = False


def _clip(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def act(obs):
    global _step, _lam, _goal, _x_est, _checked
    _step += 1
    _x_est += float(obs[5]) * DT

    # Direction sanity check: if leaning moved us backward, mirror the lean.
    if not _checked and _step >= CHECK_STEP:
        _checked = True
        if _x_est < -0.03:
            _goal = -LMAX

    pitch = float(obs[1])
    if abs(pitch) > 0.18:
        # back off the lean if torso pitch nears the health limit
        if _lam > 0:
            _lam = max(0.0, _lam - RATE)
        elif _lam < 0:
            _lam = min(0.0, _lam + RATE)
    else:
        _lam += _clip(_goal - _lam, -RATE, RATE)

    lam = _lam
    pr = PR_RATIO * lam

    q_thigh, q_leg, q_foot = float(obs[2]), float(obs[3]), float(obs[4])
    v_thigh, v_leg, v_foot = float(obs[8]), float(obs[9]), float(obs[10])

    t_thigh = pr - lam
    t_leg = 0.05      # press knee into its straight limit
    t_foot = lam

    a_thigh = 2.0 * (t_thigh - q_thigh) - 0.2 * v_thigh - 0.0346 * math.sin(pr)
    a_leg = 2.0 * (t_leg - q_leg) - 0.2 * v_leg
    a_foot = (3.0 * (t_foot - q_foot) - 0.5 * v_foot
              - 0.45 * (0.676 * math.sin(lam) + 0.0694 * math.sin(pr)))

    return [_clip(a_thigh, -1.0, 1.0),
            _clip(a_leg, -1.0, 1.0),
            _clip(a_foot, -1.0, 1.0)]
