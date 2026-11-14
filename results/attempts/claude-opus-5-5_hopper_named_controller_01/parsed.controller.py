import numpy as np

# Hopper standing-balance controller.
# Sign conventions (hopper.xml): rooty, thigh, leg and foot joints all rotate about -y,
# so a positive torso angle means leaning backward, and a positive joint torque rotates
# the child segment positively while pushing the parent segment negatively.

# Hip: keeps the torso upright (absolute torso angle).
K_HIP = 3.0
D_HIP = 0.25

# Knee: keeps the leg straight.
K_KNEE = 5.0
D_KNEE = 0.3

# Ankle: keeps the whole leg vertical over the foot (inverted-pendulum balance).
K_ANKLE = 1.5
D_ANKLE = 0.35

TORSO_TARGET = 0.0
LEG_ABS_TARGET = 0.0


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso, q_thigh, q_leg, q_foot = o[1], o[2], o[3], o[4]
    w_torso, w_thigh, w_leg, w_foot = o[7], o[8], o[9], o[10]

    # Hip: positive torque pushes the torso toward negative angle (forward).
    u_thigh = K_HIP * (torso - TORSO_TARGET) + D_HIP * w_torso

    # Knee: plain PD to a straight leg.
    u_leg = -K_KNEE * q_leg - D_KNEE * w_leg

    # Ankle: positive torque pushes the lower leg toward negative absolute angle.
    leg_abs = torso + q_thigh + q_leg
    leg_abs_dot = w_torso + w_thigh + w_leg
    u_foot = K_ANKLE * (leg_abs - LEG_ABS_TARGET) + D_ANKLE * leg_abs_dot

    a = np.clip([u_thigh, u_leg, u_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
