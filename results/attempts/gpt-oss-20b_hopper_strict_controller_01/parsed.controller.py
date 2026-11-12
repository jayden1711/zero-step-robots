# Simple deterministic controller for an unknown physics system
# ------------------------------------------------------------
# The policy uses a small forward bias, stabilises a primary angle sensor,
# and leaves the third actuator idle to avoid unnecessary penalty.
# No external state is required.

def _clip(val, low, high):
    """Clamp a value to the inclusive range [low, high]."""
    if val < low:
        return low
    if val > high:
        return high
    return val

def act(obs):
    """
    Compute a deterministic 3‑dimensional action vector from the 11‑dimensional observation.

    Parameters
    ----------
    obs : list or tuple of 11 floats
        Raw observation vector from the simulator.

    Returns
    -------
    list of 3 floats
        Action components, each will be clipped to [-1, 1] by the simulator.
    """
    # Basic sensor readings
    v_rate = obs[5]      # related rate of change (proxy for hidden velocity)
    angle = obs[1]       # primary angle or deviation from upright
    height = obs[0]      # a height‑like measurement that must stay > 0.7

    # Forward push bias – encourages positive hidden velocity
    # A small constant bias (0.1) plus a term that scales with v_rate.
    a0 = 0.1 + 0.05 * v_rate

    # Angle correction – drives the angle back toward 0.
    # The gain can be tuned; 1.0 keeps the correction moderate.
    a1 = -1.0 * angle

    # Third actuator left idle to minimise action penalty.
    a2 = 0.0

    # Optional: increase forward push slightly if the height is close to the threshold.
    if height < 0.8:
        a0 += 0.05

    # Clip each action component to [-1, 1] (the simulator will also clip them).
    a0 = _clip(a0, -1.0, 1.0)
    a1 = _clip(a1, -1.0, 1.0)
    a2 = _clip(a2, -1.0, 1.0)

    # Return actions as a list of floats.
    return [float(a0), float(a1), float(a2)]

def reset():
    """
    Reset any persistent state.  This implementation has no internal state,
    but the function is provided for API compatibility.
    """
    pass
