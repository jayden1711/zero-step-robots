```python
# InvertedPendulum controller for Gymnasium InvertedPendulum-v5
# -----------------------------------------------------------
# This controller uses a simple linear state‑feedback (PD on the pole angle
# plus a small damping term on cart position/velocity).  The parameters
# were chosen to keep the pole upright for the whole episode without
# saturating the actuator frequently.

def reset():
    """
    Reset any internal state between episodes.
    For this stateless controller this is a no‑op.
    """
    pass

def act(obs):
    """
    Compute the action for the inverted pendulum.

    Parameters
    ----------
    obs : list or tuple of 4 floats
        [cart_position, pole_angle, cart_velocity, pole_angular_velocity]

    Returns
    -------
    list
        A single‑element list containing the force to apply to the cart.
        The value is clipped to [-3, 3] by the environment automatically.
    """
    x, theta, x_dot, theta_dot = obs

    # Control gains
    #   -12*theta: PD on pole angle (stabilise upright)
    #   -6*theta_dot: damping on pole angular velocity
    #   -1*x: keep cart near the centre
    #   -1*x_dot: damp cart motion
    a = (-12.0 * theta
         - 6.0 * theta_dot
         - 1.0 * x
         - 1.0 * x_dot)

    # Clip manually just in case (optional, the env does this too)
    if a > 3.0:
        a = 3.0
    elif a < -3.0:
        a = -3.0

    return [a]
```