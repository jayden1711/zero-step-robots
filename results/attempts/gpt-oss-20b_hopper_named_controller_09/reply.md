Below is a single‑module implementation of a deterministic policy for **Hopper‑v5**.  
The controller uses a simple proportional–derivative (PD) scheme to keep the robot upright and at a desired height, while also applying a small forward push that depends on the current foot angle.  
The policy is deterministic, keeps no hidden state, and the `reset()` function is called at the start of each episode.

```python
# hopper_controller.py
# A simple deterministic controller for Gymnasium Hopper-v5

import numpy as np

# --- parameters -------------------------------------------------------------
# Target values for the robot state
TARGET_HEIGHT   = 1.00          # desired torso height (m)
TARGET_ANGLE    = 0.0           # desired torso angle (rad)
TARGET_THIGH    = 0.5           # desired thigh joint angle (rad)
TARGET_LEG      = -0.5          # desired leg joint angle (rad)
TARGET_FOOT     = 0.0           # desired foot joint angle (rad)

# Proportional/derivative gains
KP_POS   = 5.0   # height
KD_POS   = 0.5   # height derivative
KP_ANG   = 5.0   # torso angle
KD_ANG   = 0.5   # torso angle derivative
KP_JOINT = 10.0  # joint angles
KD_JOINT = 1.0   # joint angular velocities

# Extra push during stance / swing
STANCE_PULSE  = 0.3   # torque added to the leg during stance
SWING_PULSE   = 0.3   # torque added to the thigh during swing

# -----------------------------------------------------------------------------

def reset():
    """
    Reset any episode‑specific state.
    In this implementation we keep none, but the function is required by the API.
    """
    pass


def act(obs):
    """
    Compute the torques for the thigh, leg and foot joints.

    Parameters
    ----------
    obs : list or np.ndarray of length 11
        Observation vector from Hopper-v5.

    Returns
    -------
    actions : list of three floats
        Torques for thigh, leg, and foot joints in the order requested by the
        environment. Values are clipped to [-1, 1] by the environment.
    """
    # Unpack observation
    height       = obs[0]
    torso_angle  = obs[1]
    thigh_angle  = obs[2]
    leg_angle    = obs[3]
    foot_angle   = obs[4]
    # velocities
    vel_z        = obs[6]   # torso z‑velocity
    ang_vel      = obs[7]   # torso angular velocity
    th_v         = obs[9]   # thigh angular velocity
    leg_v        = obs[10]  # leg angular velocity
    foot_v       = obs[11]  # foot angular velocity

    # Height control (PD)
    h_err   = TARGET_HEIGHT - height
    h_torq  = KP_POS * h_err + KD_POS * (-vel_z)  # negative because up is +z

    # Torso angle control (PD)
    ang_err = TARGET_ANGLE - torso_angle
    ang_torq = KP_ANG * ang_err + KD_ANG * (-ang_vel)

    # Joint angle controls (PD)
    thigh_torq = KP_JOINT * (TARGET_THIGH - thigh_angle) + KD_JOINT * th_v
    leg_torq   = KP_JOINT * (TARGET_LEG   - leg_angle  ) + KD_JOINT * leg_v
    foot_torq  = KP_JOINT * (TARGET_FOOT  - foot_angle ) + KD_JOINT * foot_v

    # Add a small forward push that depends on the stance/swing phase
    # When the foot is behind the body (negative angle) it is usually in stance,
    # otherwise it is in swing.  This heuristic encourages the leg to extend
    # during stance and the thigh to swing forward during the swing phase.
    if foot_angle < 0:          # stance phase
        leg_torq += STANCE_PULSE * (-foot_angle)   # push leg back
    else:                       # swing phase
        thigh_torq += SWING_PULSE * foot_angle     # swing thigh forward

    # Combine torques for the three joints
    a1 = thigh_torq + 0.1 * ang_torq   # slight coupling to torso angle
    a2 = leg_torq   - 0.1 * ang_torq
    a3 = foot_torq

    # Clip to action bounds; the environment will clip again if necessary
    a1 = np.clip(a1, -1.0, 1.0)
    a2 = np.clip(a2, -1.0, 1.0)
    a3 = np.clip(a3, -1.0, 1.0)

    return [float(a1), float(a2), float(a3)]
```

**Notes**

* The controller is intentionally simple yet includes both balance (height and angle PD terms) and a lightweight gait generator (the stance/swing pulse).  
* All gains are tuned heuristically; they can be further tuned if desired, but the policy should already produce a reasonable forward velocity while keeping the hopper healthy.  
* The `reset()` function is present for compatibility with the Gymnasium callback pattern, even though no per‑episode state is stored.