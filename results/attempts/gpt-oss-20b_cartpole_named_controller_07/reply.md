```python
import numpy as np

# Controller gains (tuned for the InvertedPendulum-v5 dynamics)
_K_THETA = 15.0   # proportional gain on pole angle
_K_DTHETA = 2.0   # derivative gain on pole angular velocity
_K_X = 0.5        # proportional gain on cart position
_K_XD = 0.1       # derivative gain on cart velocity
_K_INT = 0.05     # integral gain on pole angle (to counteract steady‑state bias)

# Integral accumulator for the pole angle (used for a small integral action)
_integral_theta = 0.0

def reset() -> None:
    """
    Reset any internal state at the beginning of each episode.
    """
    global _integral_theta
    _integral_theta = 0.0

def act(obs):
    """
    Compute the action for the cart based on the current observation.

    Parameters
    ----------
    obs : list or tuple of 4 floats
        [cart position, pole angle, cart velocity, pole angular velocity]

    Returns
    -------
    list
        A single-element list containing the force to apply to the cart.
    """
    global _integral_theta

    # Unpack observation
    x, theta, x_dot, theta_dot = obs

    # Update integral of pole angle
    _integral_theta += theta * 0.04  # step duration is 0.04s

    # Compute raw control signal (linear state‑feedback + integral)
    u = (
        -_K_THETA * theta
        - _K_DTHETA * theta_dot
        - _K_X * x
        - _K_XD * x_dot
        + _K_INT * _integral_theta
    )

    # Clip to the action bounds [-3, 3]
    u = np.clip(u, -3.0, 3.0)

    return [float(u)]
```