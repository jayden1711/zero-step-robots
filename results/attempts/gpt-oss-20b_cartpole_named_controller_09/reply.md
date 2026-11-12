```python
"""
A simple deterministic controller for the Gymnasium InvertedPendulum-v5 environment.

The policy uses a linear state‑feedback controller that stabilises the pole around
the upright position while keeping the cart near the centre of the rail.

Author: OpenAI ChatGPT
"""

# No external state is required, but we provide a reset() stub for completeness.
def reset():
    """
    Reset any internal state (none in this controller).
    This function is called at the beginning of each episode.
    """
    pass


def act(obs):
    """
    Compute an action for the cart based on the current observation.

    Parameters
    ----------
    obs : list or tuple of 4 floats
        [cart_position, pole_angle, cart_velocity, pole_angular_velocity]

    Returns
    -------
    list of 1 float
        The force to apply to the cart, clipped to the environment's action bounds
        [-3, 3].
    """
    # Unpack the observation
    x, theta, x_dot, theta_dot = obs

    # Control gains (tuned heuristically)
    k_theta = 8.0      # Proportional on pole angle
    k_dtheta = 2.0     # Derivative on pole angular velocity
    k_pos = 1.0        # Proportional on cart position
    k_dpos = 0.1       # Derivative on cart velocity

    # Compute the raw control signal
    a = (
        -k_theta * theta
        - k_dtheta * theta_dot
        - k_pos * x
        - k_dpos * x_dot
    )

    # Clip to action limits
    if a > 3.0:
        a = 3.0
    elif a < -3.0:
        a = -3.0

    return [a]
```