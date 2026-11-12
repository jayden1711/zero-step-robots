```python
# Hopper controller for Gymnasium Hopper-v5
#
# This controller uses a simple phase‑based PD policy.
# The phase increases with every call to act(), generating a
# periodic gait pattern for the thigh, leg and foot joints.
#
# The phase speed is slightly modulated by the torso forward
# velocity to give the robot a bit of responsiveness to its
# speed.  The PD gains are chosen to keep the torques within
# the [-1, 1] range while still providing enough drive
# for forward motion.
#
# No external files or network access are required.

import numpy as np

# Global variables that persist across episode steps
_phase = 0.0          # Phase of the gait cycle (radians)
_dt = 0.008           # Simulation time step
_kp = 1.5             # Proportional gain for PD controller
_kd = 0.1             # Derivative gain for PD controller
_phase_speed = 1.5    # Base angular speed of the phase
_phase_scale = 0.8    # How much the torso velocity modulates phase speed

# Desired gait parameters (amplitude and phase shifts)
_THIGH_AMPL = 0.4
_LEG_AMPL   = 0.35
_FOOT_AMPL  = 0.25
_LEG_SHIFT  = np.pi / 2
_FOOT_SHIFT = np.pi

def reset():
    """
    Called at the beginning of each episode.
    Reset the phase to zero.
    """
    global _phase
    _phase = 0.0

def act(obs):
    """
    Compute the action for the current observation.

    Parameters
    ----------
    obs : list or array-like of shape (11,)
        Observation vector:
        0: torso height (z)
        1: torso angle (radians)
        2: thigh joint angle
        3: leg joint angle
        4: foot joint angle
        5: torso x-velocity
        6: torso z-velocity
        7: torso angular velocity
        8: thigh joint angular velocity
        9: leg joint angular velocity
        10: foot joint angular velocity

    Returns
    -------
    list of 3 floats
        Torques for thigh, leg and foot joints respectively.
    """
    global _phase

    # Convert observation to numpy array for easier indexing
    o = np.array(obs, dtype=np.float32)

    # Current joint angles and angular velocities
    thigh_angle = o[2]
    leg_angle   = o[3]
    foot_angle  = o[4]

    thigh_vel   = o[8]
    leg_vel     = o[9]
    foot_vel    = o[10]

    # Torso forward velocity influences phase speed
    torso_vel = o[5]
    phase_speed = _phase_speed + _phase_scale * torso_vel

    # Increment phase
    _phase += phase_speed * _dt
    # Keep phase bounded to avoid overflow
    _phase = np.mod(_phase, 2 * np.pi)

    # Desired angles from a sinusoidal gait pattern
    desired_thigh = _THIGH_AMPL * np.sin(_phase)
    desired_leg   = _LEG_AMPL   * np.sin(_phase + _LEG_SHIFT)
    desired_foot  = _FOOT_AMPL  * np.sin(_phase + _FOOT_SHIFT)

    # PD control law: torque = Kp * error + Kd * derivative
    a_thigh = _kp * (desired_thigh - thigh_angle) + _kd * (-thigh_vel)
    a_leg   = _kp * (desired_leg   - leg_angle)   + _kd * (-leg_vel)
    a_foot  = _kp * (desired_foot  - foot_angle)  + _kd * (-foot_vel)

    # Clip actions to the allowed range [-1, 1]
    action = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)

    # Return as a plain Python list
    return action.tolist()
```