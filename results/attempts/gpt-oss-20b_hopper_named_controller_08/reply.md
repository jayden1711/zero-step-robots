```python
import numpy as np

# Controller constants
TARGET_VELOCITY = 1.0      # desired forward speed (m/s)
KP_ANG = 1.0               # proportional gain for torso angle
KD_ANG = 0.5               # derivative gain for torso angular velocity
KP_VEL = 0.2               # proportional gain for velocity error


def act(obs):
    """
    Compute action for the Hopper-v5 environment.

    Parameters
    ----------
    obs : list[float]
        Observation vector of length 11:
        0. torso height (z)
        1. torso angle (rad)
        2. thigh joint angle
        3. leg joint angle
        4. foot joint angle
        5. torso x-velocity
        6. torso z-velocity
        7. torso angular velocity
        8. thigh joint angular velocity
        9. leg joint angular velocity
        10. foot joint angular velocity

    Returns
    -------
    list[float]
        Action vector of length 3 (torques for thigh, leg, foot).
    """
    # Extract useful observations
    torso_angle = obs[1]
    torso_ang_vel = obs[7]
    torso_x_vel = obs[6]

    # Compute velocity error relative to target forward speed
    vel_err = TARGET_VELOCITY - torso_x_vel

    # PD control for upright posture and velocity tracking
    a_thigh = -KP_ANG * torso_angle - KD_ANG * torso_ang_vel + KP_VEL * vel_err
    a_leg   =  KP_ANG * torso_angle + KD_ANG * torso_ang_vel
    a_foot  = 0.0  # no explicit foot torque

    # Clamp to action bounds [-1, 1]
    a_thigh = float(np.clip(a_thigh, -1.0, 1.0))
    a_leg   = float(np.clip(a_leg,   -1.0, 1.0))
    a_foot  = float(np.clip(a_foot,  -1.0, 1.0))

    return [a_thigh, a_leg, a_foot]


def reset():
    """
    Reset any internal state at the start of a new episode.
    (This controller has no persistent state, so the function is empty.)
    """
    pass
```
