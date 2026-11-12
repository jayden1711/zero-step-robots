import numpy as np

_step = 0

# PD gains on normalized torque (actuator gear ~200)
KP = np.array([1.5, 1.5, 1.5])
KD = np.array([0.06, 0.06, 0.06])

LEAN_START = 860
LEAN_END = 980
LEAN_MAX = 0.12
PITCH_GUARD = 0.15


def reset():
    global _step
    _step = 0


def act(obs):
    global _step
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    pitch = o[1]

    target = np.zeros(3)

    # Late-episode forward lean via the ankle (foot flat => pitch ~= sum of joint angles)
    if _step >= LEAN_START:
        frac = min(1.0, (_step - LEAN_START) / float(LEAN_END - LEAN_START))
        lean = LEAN_MAX * frac
        if abs(pitch) > PITCH_GUARD:
            # hold current posture rather than leaning further
            lean = min(lean, q[2])
        target[2] = lean

    # Torso-pitch correction: if the body tips beyond the intended lean, push back with the ankle
    desired_pitch = target[2]
    err = pitch - desired_pitch
    if abs(err) > 0.05:
        target[2] -= 0.5 * (err - np.sign(err) * 0.05)

    a = KP * (target - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)

    _step += 1
    return [float(a[0]), float(a[1]), float(a[2])]
