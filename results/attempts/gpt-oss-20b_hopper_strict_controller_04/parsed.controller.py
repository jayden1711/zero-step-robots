# Simple controller for the unknown simulated system.
# It uses two observations to generate a small stabilizing action.
# No external state or learning is required.

def act(obs):
    """
    Produce a 3‑element action vector based on the current observation.

    Parameters
    ----------
    obs : list or tuple of 11 floats
        Observation from the environment.

    Returns
    -------
    list[float]
        Action of length 3, each component clipped to [-1, 1].
    """
    # Extract relevant observations.
    # obs[5] is a related instantaneous rate of change of the unobserved x.
    # obs[1] is the angle (or similar) that must stay within [-0.2, 0.2] for health.
    rate = obs[5]
    angle = obs[1]

    # Action component 1: small proportional push in the direction of the rate.
    a1 = 0.05 * rate
    if a1 > 1.0:
        a1 = 1.0
    elif a1 < -1.0:
        a1 = -1.0

    # Action component 2: proportional controller to keep the angle near zero.
    a2 = -3.0 * angle
    if a2 > 1.0:
        a2 = 1.0
    elif a2 < -1.0:
        a2 = -1.0

    # Action component 3 is unused; set to zero.
    a3 = 0.0

    return [a1, a2, a3]

def reset():
    """
    Reset any episode‑specific state. This controller does not maintain state.
    """
    pass
