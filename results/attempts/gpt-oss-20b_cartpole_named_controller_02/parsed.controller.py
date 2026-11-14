# controller.py

import numpy as np

# Controller gains
Kp = 12.0   # Proportional gain on pole angle
Kd = 0.5    # Derivative gain on pole angular velocity
Kx = 1.0    # Gain on cart position
Kv = 0.5    # Gain on cart velocity

def act(obs):
    """
    Compute the force to apply to the cart.

    Parameters
    ----------
    obs : list or array of four floats
        [cart_pos, pole_angle, cart_vel, pole_ang_vel]

    Returns
    -------
    list
        [force] – a single float clipped to [-3, 3]
    """
    cart_pos, pole_angle, cart_vel, pole_ang_vel = obs

    # Linear state‑feedback (PD on angle + stabilizing cart terms)
    force = (
        Kp * pole_angle
        + Kd * pole_ang_vel
        - Kx * cart_pos
        - Kv * cart_vel
    )

    # Clip to action bounds
    force = float(np.clip(force, -3.0, 3.0))

    return [force]

def reset():
    """
    Reset any internal state at the start of a new episode.
    This controller has no persistent state, so this is a no‑op.
    """
    pass
