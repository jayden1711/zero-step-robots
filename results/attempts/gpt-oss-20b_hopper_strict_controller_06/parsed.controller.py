# Simple deterministic controller for an unknown physics simulation.
# The controller applies small constant torques to the first two actuators,
# which is a common baseline for many walking or balancing tasks.
# The third action is kept at zero to avoid unnecessary penalty.

def act(obs):
    """
    Compute the action for the current observation.
    
    Parameters:
        obs (list[float]): Observation vector of length 11.
    
    Returns:
        list[float]: Action vector of length 3, each value in [-1, 1].
    """
    # Constant small forward torque for the first two actuators.
    # This provides a modest push that usually keeps the system moving
    # forward while keeping the action magnitude low.
    return [0.1, 0.1, 0.0]


def reset():
    """
    Reset any internal state at the beginning of each episode.
    This controller does not maintain any state, so the function is a no-op.
    """
    pass
