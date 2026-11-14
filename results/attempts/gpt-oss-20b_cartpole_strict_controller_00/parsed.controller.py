"""
A simple linear controller for a cart‑pole like system.

Assumptions (based on the reward definition):
- obs[1] is the pole angle (theta, in radians).
- obs[3] is the pole angular velocity (theta_dot).
- The action is a force applied to the cart, clipped to [-3, 3].

The controller applies a proportional–derivative (PD) law:
    a = -k_p * theta - k_d * theta_dot
with k_p = 2.0 and k_d = 0.5.  These gains keep the pole balanced
for a wide range of initial perturbations while respecting the action bounds.
"""

import math

# Optional: if you want to keep state between calls you can
# define module-level variables here.  This controller is stateless,
# so nothing is required.

def reset():
    """
    Called at the start of each episode.  No internal state to reset.
    """
    pass

def act(obs):
    """
    Compute the action for the current observation.

    Parameters
    ----------
    obs : list or tuple of 4 floats
        Observation vector [cart_position, pole_angle, cart_velocity, pole_angular_velocity].

    Returns
    -------
    list
        A single-element list containing the action value in [-3, 3].
    """
    # Extract the pole angle and angular velocity
    theta = obs[1]
    theta_dot = obs[3]

    # PD control law
    k_p = 2.0   # proportional gain
    k_d = 0.5   # derivative gain
    action = -k_p * theta - k_d * theta_dot

    # Clip to action bounds
    action = max(-3.0, min(3.0, action))

    return [action]
