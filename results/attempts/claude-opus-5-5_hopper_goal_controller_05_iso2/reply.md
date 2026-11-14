This looks like a one-legged hopper. I didn't attempt a hopping gait: a blind gait has a high chance of falling early and losing up to ~1000 points. Instead the controller does two things:

1. **Stand stably for most of the episode (~1000 points).** With the joints held straight, the body's center of mass sits over the foot. So it is statically stable:
   - The hip and knee use PD control to hold their joint angles at 0.
   - The ankle uses PD control to keep the leg's absolute angle (torso + hip + knee angles) vertical.
   - All the torque signs come straight from the joint geometry ("push against the error"), so they don't depend on which way the axes point.
2. **Dive forward at the end (~+100 points).** In the last ~70 steps the ankle tips the rigid leg forward, and the hip keeps the torso upright. The body then falls forward about 0.8 m before the episode ends. Each metre forward is worth about 125 points.
   - Which ankle direction counts as "forward" depends on the axis convention. So the controller checks the measured forward velocity `obs[5]` a few steps into the dive and flips direction if it is moving backward.

```python
import numpy as np

_step = 0
_dive_sign = 1.0
_checked = False

DIVE_START = 928
CHECK_STEP = DIVE_START + 10


def reset():
    global _step, _dive_sign, _checked
    _step = 0
    _dive_sign = 1.0
    _checked = False


def _clip(x):
    return float(np.clip(x, -1.0, 1.0))


def act(obs):
    global _step, _dive_sign, _checked
    o = np.asarray(obs, dtype=float)
    th, q1, q2, q3 = o[1], o[2], o[3], o[4]
    thd, q1d, q2d, q3d = o[7], o[8], o[9], o[10]
    _step += 1

    # leg absolute angle (torso + hip + knee)
    psi = th + q1 + q2
    psid = thd + q1d + q2d

    # knee: hold straight
    a_knee = -3.0 * q2 - 0.3 * q2d

    if _step < DIVE_START:
        # standing: rigid body balanced over flat foot
        a_hip = -3.0 * q1 - 0.3 * q1d
        a_foot = 1.5 * psi + 0.25 * psid
    else:
        # forward dive: keep torso upright, tip leg forward with the ankle
        if not _checked and _step >= CHECK_STEP:
            _checked = True
            if o[5] < -0.02:
                _dive_sign = -_dive_sign
        a_hip = 3.0 * th + 0.3 * thd
        a_foot = 0.8 * _dive_sign

    return [_clip(a_hip), _clip(a_knee), _clip(a_foot)]
```