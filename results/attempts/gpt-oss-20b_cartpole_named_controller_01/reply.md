```python
"""
Simple deterministic controller for InvertedPendulum-v5.

The controller implements a proportional‑derivative (PD) policy that stabilises the pole
by applying a force proportional to the pole angle and its angular velocity.
The action is clipped to the allowed range [-3, 3] by the environment.

The policy is deterministic and stateless; a reset() function is provided
only to satisfy the API requirement.
"""

import numpy as np

# PD gains (tuned manually for the dynamics of InvertedPendulum-v5)
# These values work well for keeping the pole upright within the 0.2 rad tolerance
K_P = 10.0   # proportional gain on pole angle
K_D = 10.0   # derivative gain on pole angular velocity

# Action limits (as enforced by the environment)
ACTION_MIN = -3.0
ACTION_MAX =  3.0

def reset():
    """
    Called at the start of each episode.
    The controller is stateless, so nothing needs to be reset.
    """
    pass

def act(obs):
    """
    Compute the action for a single time step.

    Parameters
    ----------
    obs : list or array_like
        Observation of shape (4,):
        0. cart position (m)
        1. pole angle (rad)
        2. cart velocity (m/s)
        3. pole angular velocity (rad/s)

    Returns
    -------
    action : list
        A single-element list containing the force to apply to the cart.
    """
    # Ensure obs is a numpy array for convenient indexing
    obs = np.asarray(obs, dtype=np.float64)

    # Extract the relevant state variables
    theta = obs[1]   # pole angle
    theta_dot = obs[3]  # pole angular velocity

    # PD control law (negative sign to push the cart opposite to the pole tilt)
    a = -K_P * theta - K_D * theta_dot

    # Clip the action to the allowed range
    a = np.clip(a, ACTION_MIN, ACTION_MAX)

    # Return as a one-element list
    return [float(a)]
```