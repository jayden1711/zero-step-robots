import numpy as np

# PD controller gains for each joint
Kp_thigh = 4.0
Kd_thigh = 1.0
Kp_leg = 4.0
Kd_leg = 1.0
Kp_foot = 2.0
Kd_foot = 0.5

# Additional torques to keep the torso upright
Kp_torso = 2.0
Kd_torso = 0.5

# Desired joint angles (radians)
TARGET_THIGH = 0.0
TARGET_LEG = -0.2   # slightly bent leg to keep the torso up
TARGET_FOOT = 0.0

# Small feed‑forward push to encourage forward motion
FF_LEG = 0.05


def act(obs):
    """
    Compute the torque for the thigh, leg, and foot joints.
    obs: list or array of 11 floats as described in the task.
    Returns a list of 3 floats in the range [-1, 1].
    """
    # Unpack observations
    thigh_angle = obs[2]
    leg_angle = obs[3]
    foot_angle = obs[4]
    thigh_vel = obs[8]
    leg_vel = obs[9]
    foot_vel = obs[10]
    torso_angle = obs[1]
    torso_ang_vel = obs[7]

    # PD control for each joint
    a_thigh = Kp_thigh * (TARGET_THIGH - thigh_angle) - Kd_thigh * thigh_vel
    a_leg   = Kp_leg   * (TARGET_LEG   - leg_angle)   - Kd_leg   * leg_vel
    a_foot  = Kp_foot  * (TARGET_FOOT  - foot_angle)  - Kd_foot  * foot_vel

    # Torso correction (use the same gains for both joints for simplicity)
    torso_correction = Kp_torso * (-torso_angle) - Kd_torso * torso_ang_vel
    a_thigh += torso_correction
    a_leg   += torso_correction

    # Small forward push on the leg joint
    a_leg += FF_LEG

    # Clip actions to the valid range
    a_thigh = float(np.clip(a_thigh, -1.0, 1.0))
    a_leg   = float(np.clip(a_leg,   -1.0, 1.0))
    a_foot  = float(np.clip(a_foot,  -1.0, 1.0))

    return [a_thigh, a_leg, a_foot]


def reset():
    """
    Reset any controller state. This controller has no state,
    but the function is required by the interface.
    """
    pass
