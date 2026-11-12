# Simple proportional controller to keep obs[1] (the key state) within [-0.2, 0.2].
# The action is clipped to the allowed range [-3, 3].
# No episode‑level state is required.

def act(obs):
    """
    Parameters
    ----------
    obs : list or array_like of length 4
        The current observation from the environment.

    Returns
    -------
    action : list of length 1
        The action to apply, clipped to [-3, 3].
    """
    # Extract the observation that determines the reward
    v = obs[1]

    # Proportional control: drive the value back toward zero.
    # The gain is chosen to be large enough to correct quickly,
    # but not so large as to cause immediate clipping.
    a = -4.0 * v

    # Clip the action to the valid range
    if a > 3.0:
        a = 3.0
    elif a < -3.0:
        a = -3.0

    return [a]

# Optional: reset function (not needed here, but kept for completeness)
def reset():
    """Reset any episode‑level state (none in this controller)."""
    pass
