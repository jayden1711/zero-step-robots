"""
A lightweight deterministic controller for the Gymnasium InvertedPendulum-v5 environment.

The controller uses a linear state feedback law that acts on the pole angle and its angular velocity,
with a small correction for the cart's velocity and position.  The action is clipped to the valid
range [-3, 3] and returned as a list containing a single float, as required by the API.

The controller is stateless, but a ``reset`` function is provided so the module satisfies the
contract if a user wants to reset any future state (none is needed here).
"""

import numpy as np

# Coefficients for the linear state feedback controller.
# The state is: [cart_position, pole_angle, cart_velocity, pole_angular_velocity].
_K_CART_POS   = -0.2   # Push the cart towards the center when it drifts.
_K_CART_VEL   = -0.5   # Counteract cart motion.
_K_POLE_ANGLE = -10.0  # Strong proportional term for pole angle.
_K_POLE_ANGVEL = -1.5 # Derivative term for pole angular velocity.

def act(obs):
    """
    Compute the action for the given observation.

    Parameters
    ----------
    obs : list or array-like of 4 floats
        Observation in the order [cart position, pole angle, cart velocity, pole angular velocity].

    Returns
    -------
    list
        A single-element list containing the action to be applied, clipped to [-3, 3].
    """
    cart_pos, pole_angle, cart_vel, pole_ang_vel = obs

    # Linear state feedback law.
    action = (
        _K_CART_POS   * cart_pos +
        _K_CART_VEL   * cart_vel +
        _K_POLE_ANGLE * pole_angle +
        _K_POLE_ANGVEL * pole_ang_vel
    )

    # Clip action to the valid range and return in a list.
    clipped = np.clip(action, -3.0, 3.0)
    return [float(clipped)]

def reset():
    """
    Reset any internal state.  This implementation is stateless,
    so the function simply passes.
    """
    pass
