import numpy as np

# Joint-space PD targets (all joints straight -> rigid upright column over the foot)
_Q_TARGET = np.array([0.0, 0.0, 0.0])

_KP = np.array([4.0, 4.0, 3.0])      # stiffness per joint (action units / rad)
_KD = np.array([0.40, 0.40, 0.30])   # damping per joint (action units / (rad/s))

# Torso attitude feedback distributed over the joints (same rotation axis as joints)
_K_TORSO = 2.0
_KD_TORSO = 0.2
_TORSO_SPLIT = np.array([0.5, 0.3, 0.2])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q = o[2:5]
    torso_w = o[7]
    qd = o[8:11]

    # Hold joints stiff at the straight posture.
    a = -_KP * (q - _Q_TARGET) - _KD * qd

    # Small correction to keep the torso upright: if the torso leans with
    # positive angle, push the joints in the positive direction so the
    # torso is rotated back relative to the leg/foot on the ground.
    a += _TORSO_SPLIT * (_K_TORSO * torso_ang + _KD_TORSO * torso_w)

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
