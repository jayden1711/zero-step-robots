```python
import numpy as np

# Global phase variable used to create a simple open‑loop gait
phase = 0.0

def reset():
    """
    Reset the controller state at the beginning of each episode.
    """
    global phase
    phase = 0.0

def act(obs):
    """
    Compute action for the Hopper based on the current observation.

    Parameters
    ----------
    obs : list or array of 11 floats
        Observation from the environment:
        0  height (z) of the torso
        1  torso angle (radians)
        2  thigh joint angle
        3  leg joint angle
        4  foot joint angle
        5  torso x‑velocity
        6  torso z‑velocity
        7  torso angular velocity
        8  thigh joint angular velocity
        9  leg joint angular velocity
        10 foot joint angular velocity

    Returns
    -------
    list of 3 floats
        Actions (torques) for thigh, leg, foot joints.  Values are clipped to [-1, 1].
    """
    global phase

    # Unpack observation
    (height, tor_angle, thigh, leg, foot,
     vel_x, vel_z, ang_vel,
     thigh_vel, leg_vel, foot_vel) = obs

    # Desired joint angles: simple sinusoidal pattern
    # Amplitudes are tuned to keep the joint angles within safe ranges
    desired_thigh = 0.20 * np.sin(phase)          # roughly ±0.2 rad
    desired_leg   = -0.50 * np.cos(phase)         # roughly ±0.5 rad
    desired_foot  = 0.10 * np.sin(phase + np.pi/2)  # roughly ±0.1 rad

    # Position errors
    e_thigh = desired_thigh - thigh
    e_leg   = desired_leg   - leg
    e_foot  = desired_foot  - foot

    # PD gains (tuned empirically)
    Kp = 5.0   # proportional
    Kd = 1.0   # derivative

    # PD control torques
    a_thigh = Kp * e_thigh - Kd * thigh_vel
    a_leg   = Kp * e_leg   - Kd * leg_vel
    a_foot  = Kp * e_foot  - Kd * foot_vel

    # Additional torque to keep torso upright
    k_torso = 2.0
    a_thigh += k_torso * (-tor_angle - 0.5 * ang_vel)

    # Update phase: a slightly faster cadence when the hopper is moving forward
    phase += 0.02 * (1.0 + 0.5 * vel_x)

    # Clip actions to the valid range [-1, 1]
    actions = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)

    return actions.tolist()
```