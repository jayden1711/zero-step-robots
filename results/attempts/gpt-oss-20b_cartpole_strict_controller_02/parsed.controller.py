import numpy as np

# Simple PD controller that drives the second observation component (index 1)
# towards zero.  The action is clipped to the valid range [-3, 3].
#
# The controller uses both the value of obs[1] (the target variable) and
# obs[3] (assumed to be its derivative or a related state variable).  The
# proportional gain is 10 and the derivative gain is 5.  These values are
# chosen empirically to keep |obs[1]| within the reward band in most
# scenarios, but you can adjust them if you know more about the system.
#
# No internal state is needed between calls, so reset() is a no‑op.

def reset():
    """Called at the start of every episode. No internal state is required."""
    pass

def act(obs):
    """
    Parameters
    ----------
    obs : list or 1‑D array of 4 floats
        Observation vector.  The controller only uses obs[1] (the variable that
        must stay within [-0.2, 0.2]) and obs[3] (assumed derivative).

    Returns
    -------
    list
        A single‑element list containing the action to apply.  The value is
        automatically clipped to the allowed range [-3, 3] by the environment.
    """
    # Ensure obs has at least 4 elements; otherwise return 0 action
    if len(obs) < 4:
        return [0.0]

    # Extract the relevant states
    y  = obs[1]   # value that must stay within [-0.2, 0.2]
    dy = obs[3]   # derivative or related state

    # PD control law
    k_p = 10.0   # proportional gain
    k_d = 5.0    # derivative gain
    a = -k_p * y - k_d * dy

    # Clip to the valid action range (environment does this too, but we clip here
    # to avoid unnecessary out‑of‑range values)
    a = max(-3.0, min(3.0, a))

    return [a]
