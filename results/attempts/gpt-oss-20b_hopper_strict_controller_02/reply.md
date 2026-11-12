```python
# A simple controller that keeps the system healthy while trying to move it forward.
# It uses only the observation vector and a few proportional terms.

# No persistent state is needed, but the reset function is defined for completeness.
def reset():
    """
    Reset any controller state at the start of a new episode.
    (No state is used in this implementation.)
    """
    pass


def clamp(x, low, high):
    """Utility to clamp a value between low and high."""
    if x < low:
        return low
    if x > high:
        return high
    return x


def act(obs):
    """
    Compute the action for the current observation.

    Parameters
    ----------
    obs : list[float]
        Observation vector of length 11. Indices 5–10 are clipped to [-10, 10] in the simulator.

    Returns
    -------
    list[float]
        Action vector of length 3. Values are automatically clipped to [-1, 1] by the simulator.
    """
    # Safety: ensure we have 11 values
    if len(obs) != 11:
        raise ValueError("Expected observation of length 11")

    # Proportional control to keep the first angle (obs[1]) near 0.
    a0 = -obs[1] * 0.5

    # A small bias to keep the first state variable (obs[0]) above 0.7.
    # If it drifts below 0.7 we add a positive push.
    bias = max(0.0, 0.7 - obs[0])
    a0 += bias * 0.5

    # We want to maintain a positive forward velocity.
    # A constant forward thrust is used; this is the safest assumption.
    a2 = 0.5

    # No lateral control in this simple controller.
    a1 = 0.0

    # Clamp each action to the allowed range [-1, 1].
    a0 = clamp(a0, -1.0, 1.0)
    a1 = clamp(a1, -1.0, 1.0)
    a2 = clamp(a2, -1.0, 1.0)

    return [a0, a1, a2]
```
