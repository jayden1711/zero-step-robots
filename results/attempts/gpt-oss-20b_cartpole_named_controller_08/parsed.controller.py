import numpy as np

# Controller parameters (tuned for the InvertedPendulum-v5 dynamics)
K_P   = 10.0   # Proportional gain on pole angle
K_D   = 2.0    # Derivative gain on pole angular velocity
K_POS  = 1.0   # Proportional gain on cart position
K_POSD = 0.5   # Derivative gain on cart velocity

# The maximum and minimum force the environment accepts
FORCE_MIN = -3.0
FORCE_MAX = 3.0

def reset():
    """
    Reset any persistent state between episodes.
    This controller has no internal state, so the function is a no-op.
    """
    pass

def act(obs):
    """
    Compute the action to apply to the cart based on the current observation.

    Parameters
    ----------
    obs : list[float]
        Observation from the environment:
        [cart_position, pole_angle, cart_velocity, pole_angular_velocity]

    Returns
    -------
    list[float]
        A list containing a single force value to be applied to the cart.
    """
    # Unpack the observation
    cart_pos, pole_angle, cart_vel, pole_angular_vel = obs

    # Compute the force using a linear feedback law.
    # The goal is to keep the pole upright (pole_angle ≈ 0) and the cart near the center.
    force = (
        -K_P * pole_angle
        - K_D * pole_angular_vel
        - K_POS * cart_pos
        - K_POSD * cart_vel
    )

    # Clip the force to the action space limits.
    force = np.clip(force, FORCE_MIN, FORCE_MAX)

    return [float(force)]
