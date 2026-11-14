# Simple deterministic controller for Hopper-v5
# Author: ChatGPT
# This controller uses a lightweight PD‑like scheme with a small amount of
# state‑dependent bias to encourage forward motion while keeping the hopper
# upright and healthy.

import numpy as np

# Global state to smooth actions between steps
last_action = np.zeros(3, dtype=np.float32)


def act(obs):
    """
    Compute the next action given the observation.

    Parameters
    ----------
    obs : list or array of shape (11,)
        The observation from the environment in the order:
        [height, torso_angle, thigh, leg, foot,
         torso_x_vel, torso_z_vel, torso_ang_vel,
         thigh_vel, leg_vel, foot_vel]

    Returns
    -------
    list of 3 floats
        The torques to apply to the thigh, leg, and foot joints.
    """
    global last_action

    # Convert to numpy array for easier manipulation
    obs = np.asarray(obs, dtype=np.float32)

    # Unpack observations for readability
    height, torso_angle, thigh, leg, foot, \
    torso_x_vel, torso_z_vel, torso_ang_vel, \
    thigh_vel, leg_vel, foot_vel = obs

    # --- PD-like terms -----------------------------------------------
    # Thigh (hip) joint
    a_thigh = (-0.5 * thigh)          # position error
    a_thigh += (-0.2 * thigh_vel)    # velocity damping
    a_thigh += (-0.3 * torso_angle)  # upright bias
    a_thigh += (0.1 * torso_x_vel)   # encourage forward motion

    # Leg (knee) joint
    a_leg = (-0.3 * leg)              # position error
    a_leg += (-0.1 * leg_vel)        # velocity damping
    a_leg += (0.3 * torso_angle)     # upright bias
    a_leg += (0.3 * (0.7 - height))  # lift the body if too low

    # Foot (ankle) joint
    a_foot = (-0.1 * foot)            # position error
    a_foot += (-0.05 * foot_vel)     # velocity damping
    a_foot += (0.02 * torso_x_vel)   # small forward push

    # --- Small constant biases ---------------------------------------
    a_thigh += 0.15  # forward thrust at the hip
    a_leg   += 0.05  # slight assistance to the knee

    # Assemble raw action
    raw_action = np.array([a_thigh, a_leg, a_foot], dtype=np.float32)

    # Smooth with previous action to reduce jitter
    smoothed = 0.8 * last_action + 0.2 * raw_action
    smoothed = np.clip(smoothed, -1.0, 1.0)  # respect action bounds

    # Update the global state
    last_action = smoothed

    return smoothed.tolist()


def reset():
    """
    Reset any controller state at the start of an episode.
    """
    global last_action
    last_action = np.zeros(3, dtype=np.float32)
