import numpy as np

# The controller does not need any persistent state, but the interface allows a reset.
def reset():
    """Reset the controller state. This implementation has no state, so this is a no‑op."""
    pass

def act(obs):
    """
    Simple deterministic controller for Hopper-v5.
    
    Parameters
    ----------
    obs : list or array-like of length 11
        [height z, torso angle, thigh joint angle, leg joint angle, foot joint angle,
         torso x‑velocity, torso z‑velocity, torso angular velocity,
         thigh joint angular velocity, leg joint angular velocity, foot joint angular velocity]
    
    Returns
    -------
    action : list of 3 floats
        Torques applied at thigh, leg, and foot joints (clipped to [-1, 1]).
    """
    # Convert to a numpy array for easier indexing
    o = np.asarray(obs, dtype=np.float32)

    # Extract relevant observations for readability
    height = o[0]
    torso_ang = o[1]
    thigh_ang = o[2]
    leg_ang = o[3]
    foot_ang = o[4]
    torso_vx = o[5]
    torso_vz = o[6]
    torso_ang_vel = o[7]
    thigh_ang_vel = o[8]
    leg_ang_vel = o[9]
    foot_ang_vel = o[10]

    # --- Control logic ----------------------------------------------------
    # Target height (roughly the nominal torso height in the training data)
    target_height = 1.0

    # Thigh torque:
    #   - Oppose torso tilt and angular velocity to keep upright.
    #   - Add a height restoring term if the torso is below target.
    #   - Slight damping on the thigh joint velocity.
    thigh_torque = (
        -5.0 * torso_ang           # PD on torso angle
        -0.1 * torso_ang_vel
        -0.1 * thigh_ang_vel
        + 1.5 * (target_height - height)  # height correction
    )

    # Leg torque:
    #   - Constant bias to keep the leg in a slightly forward position.
    #   - Small feedforward from torso forward velocity to encourage stepping.
    leg_torque = 0.3 + 0.2 * torso_vx

    # Foot torque:
    #   - Keep the foot close to zero angle (roughly horizontal).
    #   - Damping on foot angular velocity.
    foot_torque = -0.8 * foot_ang - 0.1 * foot_ang_vel

    # --- Clip actions to [-1, 1] ----------------------------------------
    action = np.clip([thigh_torque, leg_torque, foot_torque], -1.0, 1.0)

    return action.tolist()
