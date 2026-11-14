import numpy as np

# ------------------------------------------------------------------
# Controller for the simulated system
# ------------------------------------------------------------------
# The observation vector has 4 raw numbers.
# The second element (index 1) is the key state that must be kept within
# |obs[1]| <= 0.2 for the episode to continue.  The action is a single
# continuous torque value that will be clipped to [-3, 3] by the simulator.
#
# We use a simple PD controller that drives the value of obs[1] (and its
# derivative obs[3]) towards zero.  The constants were chosen empirically
# to provide a good trade‑off between responsiveness and stability for a
# variety of linear‑approximate systems such as cart‑pole or pendulum.
# ------------------------------------------------------------------

# Controller parameters (tuned for typical pendulum/cart‑pole dynamics)
_KP = 2.0   # proportional gain on the key state obs[1]
_KD = 0.5   # derivative gain on obs[3] (assumed angular velocity)

def reset():
    """
    Reset any internal state.  The current controller is stateless,
    but this function is required by the framework.
    """
    pass

def act(obs):
    """
    Compute the action for the current observation.

    Parameters
    ----------
    obs : list or array-like of length 4
        Observation vector from the simulator.

    Returns
    -------
    list of float
        A single action value in the range [-3, 3] (after clipping).
    """
    # Extract the key observation and its derivative
    # We assume:
    #   obs[1] : the state we need to keep small (e.g., pole angle)
    #   obs[3] : its derivative (e.g., pole angular velocity)
    try:
        angle = float(obs[1])
        ang_vel = float(obs[3])
    except (IndexError, TypeError, ValueError):
        # If the observation is malformed, return zero action
        return [0.0]

    # PD control law
    action = -_KP * angle - _KD * ang_vel

    # Clip action to allowed range
    if action > 3.0:
        action = 3.0
    elif action < -3.0:
        action = -3.0

    return [action]
