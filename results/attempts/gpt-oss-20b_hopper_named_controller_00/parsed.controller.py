import numpy as np

# ---------- controller parameters ----------
# Desired nominal states
DESIRED_HEIGHT = 1.0          # desired torso height (z)
DESIRED_THIGH  = 0.0          # desired thigh joint angle (hip)
DESIRED_LEG    = -0.5         # desired leg joint angle (knee)
DESIRED_FOOT   = 0.0          # desired foot joint angle (ankle)

# Proportional gains for each state variable
KP_HEIGHT = 0.5
KP_THIGH  = 5.0
KP_LEG    = 5.0
KP_FOOT   = 3.0

# Derivative (velocity) gains for joint torques
KD_THIGH  = 2.0
KD_LEG    = 2.0
KD_FOOT   = 1.0

# Feed‑forward terms to help forward motion and upright posture
FF_XVEL   = 0.1   # influence of torso x‑velocity on thigh & leg
FF_ANGLE  = 0.2   # influence of torso angle on thigh & leg
FF_AVEL   = 0.1   # influence of torso angular velocity on thigh & leg

# ---------------------------------------------------------------

def _clip(a, low=-1.0, high=1.0):
    """Clamp a scalar to the given interval."""
    return float(max(min(a, high), low))

def act(obs):
    """
    Compute a deterministic action for the Hopper-v5 environment.

    Parameters
    ----------
    obs : list or array-like of shape (11,)
        Observation vector containing:
        0: torso height
        1: torso angle
        2: thigh angle
        3: leg angle
        4: foot angle
        5: torso x‑velocity
        6: torso z‑velocity
        7: torso angular velocity
        8: thigh angular velocity
        9: leg angular velocity
       10: foot angular velocity

    Returns
    -------
    list of three floats: action for thigh, leg and foot torques.
    """
    # Convert to numpy array for easier indexing
    o = np.asarray(obs, dtype=np.float64)

    # Errors relative to desired nominal states
    e_height = DESIRED_HEIGHT - o[0]
    e_thigh  = DESIRED_THIGH  - o[2]
    e_leg    = DESIRED_LEG    - o[3]
    e_foot   = DESIRED_FOOT   - o[4]

    # Base PD control terms
    a_thigh = (KP_HEIGHT * e_height +
               KP_THIGH  * e_thigh -
               KD_THIGH  * o[8])   # o[8] = thigh angular velocity

    a_leg   = (KP_LEG    * e_leg -
               KD_LEG    * o[9])   # o[9] = leg angular velocity

    a_foot  = (KP_FOOT   * e_foot -
               KD_FOOT   * o[10])  # o[10] = foot angular velocity

    # Feed‑forward terms to push forward and stay upright
    a_thigh += FF_XVEL * o[5]      # torso x‑velocity
    a_leg   += FF_XVEL * o[5] * -1.0

    a_thigh += FF_ANGLE * o[1]     # torso angle
    a_leg   += FF_ANGLE * o[1] * 0.5

    a_thigh += FF_AVEL * o[7]      # torso angular velocity
    a_leg   += FF_AVEL * o[7] * 0.5

    # Clip actions to valid range [-1, 1]
    return [_clip(a_thigh), _clip(a_leg), _clip(a_foot)]

def reset():
    """
    Reset any internal state before a new episode.
    (No internal state in this controller, so this is a no‑op.)
    """
    pass
