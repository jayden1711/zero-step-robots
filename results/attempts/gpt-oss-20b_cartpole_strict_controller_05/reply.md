```python
import numpy as np

# Controller gains
# These values were chosen empirically to provide a simple stabilising action
# that keeps the cart velocity close to zero while also countering pole
# tilting.  The gains are positive so that the action always opposes the
# current velocity and angle.
_KV = 10.0   # velocity gain
_KTHETA = 5.0   # pole angle gain
_MAX_ACTION = 3.0   # action clipping bounds (as specified by the environment)

def act(obs):
    """
    Compute a control action for the cart-pole environment.

    Parameters
    ----------
    obs : list or array-like of length 4
        Observation vector [x, x_dot, theta, theta_dot].
        x      : cart position
        x_dot  : cart velocity (index 1)
        theta  : pole angle (index 2)
        theta_dot : pole angular velocity

    Returns
    -------
    list of float
        One action value in the range [-3, 3].
    """
    # Convert to numpy array for easier indexing
    o = np.asarray(obs, dtype=float)

    # Extract the relevant state components
    x_dot = o[1]       # cart velocity
    theta = o[2]       # pole angle

    # Simple proportional controller that opposes both velocity and tilt.
    # The action is scaled by the gains and clipped to the valid range.
    action = -(x_dot * _KV + theta * _KTHETA)

    # Clip action to the environment limits
    action = np.clip(action, -_MAX_ACTION, _MAX_ACTION)

    return [float(action)]

def reset():
    """
    Optional reset hook.  This controller does not keep any internal state,
    so reset simply returns None.  The function is defined to satisfy the
    interface when a controller might need stateful behaviour.
    """
    return None
```