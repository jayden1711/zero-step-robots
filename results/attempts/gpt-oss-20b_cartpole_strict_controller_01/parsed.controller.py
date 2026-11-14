"""
A simple deterministic controller for a 4‑dimensional observation space.

The goal is to keep the second observation component (obs[1]) within
[-0.2, 0.2] for as many steps as possible.  The only control we have is a
single action that is clipped to [-3, 3].

Strategy
--------
We treat obs[1] as a velocity that we want to damp to zero.  A
proportional controller that applies a force proportional to the
negative of the velocity is sufficient to keep the system stable.

The controller is stateless; no memory is needed because the system
does not require integral action for the reward criterion.  The
`reset()` function is provided for compatibility with environments
that call it at episode start, but it does nothing.

Author: ChatGPT
"""

def act(obs):
    """
    Compute the action given an observation.

    Parameters
    ----------
    obs : list or tuple of 4 floats
        The current observation vector.

    Returns
    -------
    list of 1 float
        The action to apply, clipped to the range [-3, 3].
    """
    # Proportional gain
    Kp = 2.0

    # Desired target for obs[1] is 0.0
    target = 0.0

    # Proportional control: a = -Kp * (obs[1] - target)
    a = -Kp * (obs[1] - target)

    # Clip to the valid action range
    if a > 3.0:
        a = 3.0
    elif a < -3.0:
        a = -3.0

    return [a]


def reset():
    """
    Reset any stateful information at the start of a new episode.
    This controller is stateless, so nothing needs to be done.
    """
    pass
