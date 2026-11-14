# Simple deterministic controller for the unknown physics simulation.
# The goal is to keep obs[0] > 0.7 and |obs[1]| < 0.2 for as long as possible.
# We use a lightweight proportional controller that tries to move obs[0] toward a
# target of 1.0 (well above the 0.7 threshold) and dampen obs[1] toward 0.
# No internal state is required, but a reset() function is provided for
# consistency with the interface.

import math

def reset():
    """
    Called at the start of each episode.  No persistent state is needed,
    but this function is required by the evaluation harness.
    """
    pass

def act(obs):
    """
    Compute an action vector [a0, a1, a2] from the observation vector.

    Parameters
    ----------
    obs : list or iterable of 11 floats
        Current observation from the simulator.

    Returns
    -------
    list of 3 floats
        The action to apply.  Values outside [-1, 1] are automatically clipped
        by the simulator, but we clip explicitly for safety.
    """
    # Desired target for obs[0] (ensure it stays comfortably above 0.7)
    target_pos = 1.0

    # Proportional control gains (tuned for gentle actions to reduce penalty)
    k_pos = 0.3      # gain for the position error
    k_vel = 0.3      # gain for the velocity-like term obs[1]

    # Compute errors
    pos_error = target_pos - obs[0]   # positive if obs[0] is below target
    vel_error = -obs[1]               # positive if obs[1] is negative (want to bring it to zero)

    # Compute raw actions
    a0 = k_pos * pos_error
    a1 = k_vel * vel_error
    a2 = 0.0

    # Clip each action to the allowed range [-1, 1]
    a0 = max(-1.0, min(1.0, a0))
    a1 = max(-1.0, min(1.0, a1))
    # a2 is already zero

    return [a0, a1, a2]
