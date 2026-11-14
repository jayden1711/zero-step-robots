```python
"""
Simple deterministic controller for the InvertedPendulum-v5 environment.

The controller uses a proportional‑derivative (PD) law on the pole angle and
velocity, with additional terms that keep the cart near the centre of the rail.
The action is clipped to the admissible range [-3, 3].

The controller is stateless, but a no‑op reset() function is provided for API
compatibility.
"""

# Gain values. These were tuned manually to achieve a balance between
# fast pole stabilization and limited cart movement.
_KP_ANGLE = 10.0      # proportional gain on pole angle (rad)
_KD_ANGLE = 3.0       # derivative gain on pole angular velocity (rad/s)
_KP_POS   = 5.0       # proportional gain on cart position (m)
_KD_POS   = 1.0       # derivative gain on cart velocity (m/s)

# Action limits for the environment.
_MAX_FORCE = 3.0
_MIN_FORCE = -3.0

def act(obs):
    """
    Compute the action for a single time step.

    Parameters
    ----------
    obs : list or tuple of float, length 4
        The observation from the environment:
        [cart_position, pole_angle, cart_velocity, pole_angular_velocity]

    Returns
    -------
    list of float
        A list containing one action value. The value is clipped to the
        allowed range [-3, 3].
    """
    # Unpack observation
    x, theta, x_dot, theta_dot = obs

    # PD control law
    force = (
        -_KP_ANGLE * theta
        -_KD_ANGLE * theta_dot
        -_KP_POS   * x
        -_KD_POS   * x_dot
    )

    # Clamp force to admissible bounds
    if force > _MAX_FORCE:
        force = _MAX_FORCE
    elif force < _MIN_FORCE:
        force = _MIN_FORCE

    return [float(force)]

def reset():
    """
    Reset function called at the start of each episode.

    This controller does not keep any internal state, so the reset is a no‑op.
    """
    pass
```