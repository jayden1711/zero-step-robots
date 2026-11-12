Here is a simple deterministic controller for `Hopper-v5`.  
The policy uses a proportional‑derivative (PD) scheme on the thigh, leg and foot joints to keep the robot upright and to generate a forward gait.  
No additional learning or external data are required.

```python
# hopper_controller.py

"""
A simple PD‑based controller for the Hopper-v5 environment.

The controller tries to:
1. Keep the torso upright by controlling joint angles.
2. Generate a forward gait by adding a small bias when the torso
   forward velocity is below a target value.

This is intentionally lightweight and deterministic – it contains no
learned parameters beyond the hand‑picked PD gains.
"""

import numpy as np

# PD gains for thigh, leg, and foot joints (hand‑tuned)
_KP_THIGH = 6.0
_KD_THIGH = 1.5

_KP_LEG   = 8.0
_KD_LEG   = 2.0

_KP_FOOT  = 4.0
_KD_FOOT  = 1.5

# Target joint angles (radians) for a nominal standing/walking pose
_THIGH_TARGET = -0.30
_LEG_TARGET   = -1.00
_FOOT_TARGET  = 0.0

# Desired forward velocity (m/s) that we try to maintain
_DESIRED_X_VEL = 1.5


def reset():
    """
    Reset any internal state.  This controller has none, but the function
    is required by the interface.
    """
    pass


def act(obs):
    """
    Compute the action for the Hopper based on the observation.

    Parameters
    ----------
    obs : list[float]
        Observation vector of length 11:
        [torso_height, torso_angle, thigh_angle, leg_angle, foot_angle,
         torso_x_vel, torso_z_vel, torso_ang_vel,
         thigh_ang_vel, leg_ang_vel, foot_ang_vel]

    Returns
    -------
    list[float]
        Action vector of length 3 (torques for thigh, leg, foot),
        each clipped to [-1, 1].
    """
    # Unpack relevant observation components
    thigh_angle      = obs[2]
    leg_angle        = obs[3]
    foot_angle       = obs[4]
    thigh_ang_vel    = obs[8]
    leg_ang_vel      = obs[9]
    foot_ang_vel     = obs[10]
    torso_angle      = obs[1]
    torso_ang_vel    = obs[7]
    torso_x_vel      = obs[5]

    # ----- PD control for each joint -----
    a_thigh = (
        _KP_THIGH * (_THIGH_TARGET - thigh_angle)
        - _KD_THIGH * thigh_ang_vel
    )

    a_leg = (
        _KP_LEG * (_LEG_TARGET - leg_angle)
        - _KD_LEG * leg_ang_vel
    )

    a_foot = (
        _KP_FOOT * (_FOOT_TARGET - foot_angle)
        - _KD_FOOT * foot_ang_vel
    )

    # ----- Upright torque correction using torso angle -----
    # Small proportional and derivative terms on torso angle to keep upright
    upright_thrust = -0.3 * torso_angle - 0.1 * torso_ang_vel
    a_thigh += upright_thrust
    a_leg   += upright_thrust

    # ----- Forward velocity bias -----
    # If the hopper is moving too slowly, add a small bias to extend joints
    vel_error = _DESIRED_X_VEL - torso_x_vel
    if vel_error > 0.0:
        bias = 0.1 * vel_error  # scale bias with how far we are from target
        a_thigh += bias
        a_leg   += bias

    # Clip actions to allowed range [-1, 1]
    a_thigh = np.clip(a_thigh, -1.0, 1.0)
    a_leg   = np.clip(a_leg,   -1.0, 1.0)
    a_foot  = np.clip(a_foot,  -1.0, 1.0)

    return [float(a_thigh), float(a_leg), float(a_foot)]
```

**How to use**

```python
import hopper_controller

env = gym.make("Hopper-v5")
obs = env.reset()
while True:
    action = hopper_controller.act(obs)
    obs, reward, done, _ = env.step(action)
    if done:
        break
```

The controller is fully deterministic, uses only standard library and NumPy, and respects all constraints of the task.