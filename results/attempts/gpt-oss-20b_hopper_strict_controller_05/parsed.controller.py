# A simple deterministic controller for the unknown simulated system.
# The policy keeps the system healthy by controlling the first two action
# channels and uses a small velocity estimate from obs[5] to drive forward.
#
# The controller does not maintain any internal state between calls.
# A reset() function is provided as a no‑op so the framework can call it.

import math

def act(obs):
    """
    Compute an action vector of length 3 based on the current observation.
    
    Parameters
    ----------
    obs : list or tuple of 11 floats
        The current observation vector.
    
    Returns
    -------
    list[float]
        The action to apply. Values are clipped to [-1, 1] by the environment.
    """
    # Extract useful components from the observation.
    x_pos = obs[0]          # must stay > 0.7 to remain healthy
    tilt = obs[1]           # |tilt| must stay < 0.2
    v_est = obs[5]          # approximate instantaneous rate of change
    
    # --- Controller design -------------------------------------------
    # We keep x_pos around 0.75 by applying a proportional force.
    # A small contribution from the velocity estimate helps keep forward
    # momentum without overshooting.
    kx_pos = 2.0            # proportional gain for x position
    kv    = 0.3             # weight for velocity estimate
    a0 = kx_pos * (0.75 - x_pos) + kv * v_est
    
    # Tilt is controlled with a PD-like law; only proportional term is used
    # because we have no direct measurement of angular velocity.
    k_tilt = -5.0           # proportional gain for tilt correction
    a1 = k_tilt * tilt
    
    # The third action channel is left unused; we set it to zero.
    a2 = 0.0
    
    # Clip actions to the valid range [-1, 1].
    a0 = max(min(a0, 1.0), -1.0)
    a1 = max(min(a1, 1.0), -1.0)
    a2 = max(min(a2, 1.0), -1.0)
    
    return [a0, a1, a2]

def reset():
    """
    Reset any internal state before starting a new episode.
    This controller has no state, so the function does nothing.
    """
    pass
