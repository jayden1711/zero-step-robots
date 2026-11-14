Below is a simple deterministic controller for the Hopper‑v5 environment.  
It uses a small hand‑crafted PD policy that keeps the torso upright, the joints near
zero, and pushes the hopper forward with a modest feed‑forward term.  
The controller does not keep any internal state, but a `reset()` function is provided
for completeness.  

```python
import numpy as np

# Coefficients for the PD controllers
# These values were chosen empirically to keep the torques small while
# maintaining stability and a modest forward speed.
KP_TORSO_ANGLE = -0.3   # correction for torso tilt
KP_THIGH   = -1.0       # joint angle error for thigh
KD_THIGH   = -0.5       # joint velocity error for thigh
KP_LEG     = -1.0       # joint angle error for leg
KD_LEG     = -0.5       # joint velocity error for leg
KP_FOOT    = -1.0       # joint angle error for foot
KD_FOOT    = -0.5       # joint velocity error for foot

# Desired forward speed (m/s) and a small feed‑forward term
DESIRED_VX   = 0.5
FORWARD_GAIN = 0.1

# Height threshold for a small upward push
HEIGHT_THRESHOLD = 1.1
HEIGHT_GAINS     = 0.2

def reset():
    """
    Called at the start of each episode.  The controller is stateless,
    so this function simply passes.
    """
    pass

def act(obs):
    """
    Compute the torques for the thigh, leg, and foot joints.

    Parameters
    ----------
    obs : list or array of length 11
        Observation from the environment:
          0 : torso height (z)
          1 : torso angle (radians)
          2 : thigh joint angle
          3 : leg joint angle
          4 : foot joint angle
          5 : torso x‑velocity
          6 : torso z‑velocity
          7 : torso angular velocity
          8 : thigh joint angular velocity
          9 : leg joint angular velocity
          10: foot joint angular velocity

    Returns
    -------
    list[float]
        A list of three torques [torque_thigh, torque_leg, torque_foot].
        Values are clipped to [-1, 1] by the environment.
    """
    # Unpack the observation
    h   = obs[0]  # torso height
    th  = obs[1]  # torso angle
    ta  = obs[2]  # thigh joint angle
    la  = obs[3]  # leg joint angle
    f_a = obs[4]  # foot joint angle
    vx  = obs[5]  # torso x‑velocity
    # Other velocities are not used directly but can be added if desired
    th_v = obs[8]
    la_v = obs[9]
    f_v  = obs[10]

    # Base PD torques to keep joints near zero and torso upright
    torque_thigh = (KP_TORSO_ANGLE * th
                    + KP_THIGH * ta
                    + KD_THIGH * th_v)

    torque_leg   = (KP_LEG * la
                    + KD_LEG * la_v)

    torque_foot  = (KP_FOOT * f_a
                    + KD_FOOT * f_v)

    # Height correction: push upward if the hopper is too low
    if h < HEIGHT_THRESHOLD:
        torque_thigh += HEIGHT_GAINS

    # Forward speed correction: gently push the thigh forward
    torque_thigh += FORWARD_GAIN * (DESIRED_VX - vx)

    # Ensure the torques are within [-1, 1] (the environment will clip as well)
    torque_thigh = float(np.clip(torque_thigh, -1.0, 1.0))
    torque_leg   = float(np.clip(torque_leg,   -1.0, 1.0))
    torque_foot  = float(np.clip(torque_foot,  -1.0, 1.0))

    return [torque_thigh, torque_leg, torque_foot]
```

**How it works**

* The PD terms keep the torso upright (`KP_TORSO_ANGLE`) and keep each joint near zero.
* A small upward push (`HEIGHT_GAINS`) activates when the torso height falls below a threshold,
  helping to avoid falling.
* A forward‑speed correction (`FORWARD_GAIN`) nudges the thigh joint to produce a modest
  forward velocity, encouraging movement while keeping the torque penalty low.
* All torques are clipped to the allowed range.

Feel free to adjust the coefficient values if you find the hopper too slow or unstable
in practice.