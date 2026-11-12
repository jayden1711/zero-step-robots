# Simple PID controller aimed at keeping obs[1] close to zero.
# The controller uses the previous error to compute a derivative term.
# It also includes a small correction based on obs[2] (which might be an angle).
# All actions are clipped to the allowed range [-3, 3].

from typing import List

# Global state
prev_error: float | None = None
DT = 0.04          # Time step duration (seconds)
Kp = 6.0           # Proportional gain for obs[1]
Kd = 2.0           # Derivative gain for obs[1]
angle_weight = 0.5  # Weight for obs[2] (if it represents an angle)

def reset() -> None:
    """Reset controller state at the beginning of each episode."""
    global prev_error
    prev_error = None

def act(obs: List[float]) -> List[float]:
    """
    Compute the action for the given observation.

    Parameters
    ----------
    obs : list of float
        Observation vector of length 4. The controller focuses on obs[1]
        and optionally on obs[2].

    Returns
    -------
    list of float
        Action list containing a single float value in the range [-3, 3].
    """
    global prev_error

    # Ensure obs has at least 3 elements (obs[1] and obs[2] are used)
    if len(obs) < 3:
        raise ValueError("Observation must contain at least 3 elements.")

    # Error for the target (keep obs[1] close to zero)
    error = -obs[1]

    # Derivative term (difference from previous error)
    if prev_error is None:
        derivative = 0.0
    else:
        derivative = (error - prev_error) / DT

    # PID output plus a small correction based on obs[2] (angle)
    action = Kp * error + Kd * derivative - angle_weight * obs[2]

    # Clip to valid action range
    if action > 3.0:
        action = 3.0
    elif action < -3.0:
        action = -3.0

    # Update previous error for next step
    prev_error = error

    return [action]
