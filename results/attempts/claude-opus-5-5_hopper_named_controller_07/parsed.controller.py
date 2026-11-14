import numpy as np

DT = 0.008

_step = 0
_x = 0.0
_sign = 1.0
_target = 0.0


def reset():
    global _step, _x, _sign, _target
    _step = 0
    _x = 0.0
    _sign = 1.0
    _target = 0.0


def _ramp(t, t0, t1, v0, v1):
    if t <= t0:
        return v0
    if t >= t1:
        return v1
    a = (t - t0) / float(t1 - t0)
    # smoothstep for gentle accelerations
    a = a * a * (3.0 - 2.0 * a)
    return v0 + (v1 - v0) * a


def act(obs):
    global _step, _x, _sign, _target
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q_thigh, q_leg, q_foot = o[2], o[3], o[4]
    vx = o[5]
    qd_thigh, qd_leg, qd_foot = o[8], o[9], o[10]

    t = _step
    _x += vx * DT

    probe = 0.04
    final = 0.12

    # Lean schedule (in foot-joint angle; with the foot flat, this equals body tilt)
    if t < 60:
        target = 0.0
    elif t < 200:
        target = _ramp(t, 60, 180, 0.0, probe)
    else:
        if t == 200:
            # decide which ankle direction moves the torso forward
            _sign = 1.0 if _x >= 0.0 else -1.0
        target = _ramp(t, 200, 450, probe, _sign * final)

    # Safety guard: back off if the torso tilt gets near the 0.2 rad limit
    if abs(torso_ang) > 0.15:
        target *= 0.5
    _target = target

    # Hip and knee: hold straight against the upper joint limit (0 rad)
    a0 = 0.5 + 5.0 * (0.0 - q_thigh) - 0.1 * qd_thigh
    a1 = 0.5 + 5.0 * (0.0 - q_leg) - 0.1 * qd_leg

    # Ankle: stiff PD to the lean target
    a2 = 4.0 * (target - q_foot) - 0.15 * qd_foot

    _step += 1
    return [float(np.clip(a0, -1.0, 1.0)),
            float(np.clip(a1, -1.0, 1.0)),
            float(np.clip(a2, -1.0, 1.0))]
