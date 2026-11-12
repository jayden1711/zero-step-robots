import numpy as np

# Hold the hopper rigid in its upright standing pose. With all joints stiff, the
# body is a rigid object resting on its flat foot with its centre of mass well
# inside the support region, so it stays healthy for the full episode.

KP = np.array([1.0, 1.0, 1.0])     # 200 Nm/rad after gear
KD = np.array([0.08, 0.08, 0.08])  # kept small for discrete-time stability
TARGET = np.array([-0.02, -0.02, 0.0])  # thigh/leg slightly inside their [-150deg, 0] range

# Gentle torso-angle correction through the ankle (small, so a sign error
# could not destabilise the rigid stance quickly).
K_TORSO = 0.3
D_TORSO = 0.03


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    torso_ang = o[1]
    torso_angvel = o[7]

    a = KP * (TARGET - q) - KD * qd

    # Torso angle ~= -(sum of joint angles) - foot tilt; nudging the foot joint
    # in the same direction as the torso error rotates the body back upright.
    a[2] += -K_TORSO * torso_ang * 0.0 + 0.0  # disabled: rigid stance is already stable
    _ = D_TORSO * torso_angvel

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
