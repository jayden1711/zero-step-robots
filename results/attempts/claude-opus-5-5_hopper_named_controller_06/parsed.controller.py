import numpy as np

# Approximate Hopper-v5 segment masses (kg)
M_TORSO = 3.67
M_THIGH = 4.06
M_LEG = 2.78
M_ABOVE = M_TORSO + M_THIGH + M_LEG

# Heights of segment centres above the ankle when standing straight (m)
H_COM = (M_TORSO * 1.15 + M_THIGH * 0.725 + M_LEG * 0.25) / M_ABOVE

# Joint PD gains (action units per rad, per rad/s)
KP_JOINT = 3.0
KD_JOINT = 0.15
JOINT_TARGET = 0.03  # slightly into the 0 limit so the leg stays locked straight

# Ankle balance gains
KP_ANKLE = 2.0
KD_ANKLE = 0.3
ANKLE_LIMIT = 0.3


def reset():
    pass


def _com_angle(th0, thT, thL):
    # Horizontal centre-of-mass offset above the ankle, as an equivalent pendulum angle
    x_torso = 0.5 * thL + 0.45 * thT + 0.2 * th0
    x_thigh = 0.5 * thL + 0.225 * thT
    x_leg = 0.25 * thL
    s = M_TORSO * x_torso + M_THIGH * x_thigh + M_LEG * x_leg
    return s / (M_ABOVE * H_COM)


def act(obs):
    o = np.asarray(obs, dtype=float)
    rooty, thigh, leg = o[1], o[2], o[3]
    rooty_d, thigh_d, leg_d = o[7], o[8], o[9]

    # Absolute segment angles and rates (all joints share the same axis)
    th0, thT, thL = rooty, rooty + thigh, rooty + thigh + leg
    w0, wT, wL = rooty_d, rooty_d + thigh_d, rooty_d + thigh_d + leg_d

    phi = _com_angle(th0, thT, thL)
    phi_d = _com_angle(w0, wT, wL)

    a_thigh = KP_JOINT * (JOINT_TARGET - thigh) - KD_JOINT * thigh_d
    a_leg = KP_JOINT * (JOINT_TARGET - leg) - KD_JOINT * leg_d

    # Ankle strategy: positive foot torque pushes the leg back toward phi = 0
    a_foot = KP_ANKLE * phi + KD_ANKLE * phi_d
    a_foot = float(np.clip(a_foot, -ANKLE_LIMIT, ANKLE_LIMIT))

    return [float(np.clip(a_thigh, -1.0, 1.0)),
            float(np.clip(a_leg, -1.0, 1.0)),
            a_foot]
