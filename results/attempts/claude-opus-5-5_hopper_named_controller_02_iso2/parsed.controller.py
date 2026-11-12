import numpy as np

DT = 0.008
KP = np.array([4.0, 4.0, 4.0])
KD = np.array([0.3, 0.3, 0.3])

SETTLE_STEPS = 60
RAMP_RATE = 0.002
PROBE_LEAN = 0.12
PROBE_DISP = 0.03
LEAN_MAX = 0.36
LUNGE_STEP = 960
LUNGE_LEAN = 0.75
LUNGE_RATE = 0.01

_step = 0
_xdisp = 0.0
_lean = 0.0
_mode = "settle"


def reset():
    global _step, _xdisp, _lean, _mode
    _step = 0
    _xdisp = 0.0
    _lean = 0.0
    _mode = "settle"


def _approach(value, target, rate):
    if value < target:
        return min(value + rate, target)
    return max(value - rate, target)


def act(obs):
    global _step, _xdisp, _lean, _mode
    obs = np.asarray(obs, dtype=float)
    _step += 1
    _xdisp += obs[5] * DT

    if _mode == "settle":
        _lean = 0.0
        if _step >= SETTLE_STEPS:
            _mode = "probe"
            _xdisp = 0.0
    elif _mode == "probe":
        _lean = _approach(_lean, PROBE_LEAN, RAMP_RATE)
        if _xdisp > PROBE_DISP:
            _mode = "good"
        elif _xdisp < -PROBE_DISP:
            _mode = "bad"
        elif _lean >= PROBE_LEAN and _step > SETTLE_STEPS + 200:
            # No clear forward motion: play it safe.
            _mode = "bad"
    elif _mode == "good":
        if _step >= LUNGE_STEP:
            _lean = _approach(_lean, LUNGE_LEAN, LUNGE_RATE)
        else:
            _lean = _approach(_lean, LEAN_MAX, RAMP_RATE)
    else:  # "bad"
        _lean = _approach(_lean, 0.0, RAMP_RATE)

    # Joint targets sum to zero so the torso stays parallel to the flat foot.
    q_target = np.array([-_lean, 0.0, _lean])
    q = obs[2:5]
    qd = obs[8:11]
    u = KP * (q_target - q) - KD * qd
    u = np.clip(u, -1.0, 1.0)
    return [float(u[0]), float(u[1]), float(u[2])]
