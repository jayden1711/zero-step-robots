This controller is the safe option: it tries to stand still for all 1000 steps rather than walk or hop. I couldn't run or test it, so I can't confirm the score. If it survives every episode, it should score about 1000 per episode: roughly 1 per step, minus a tiny action cost and some forward/backward speed. A hopping gait could earn more, but one I can't test would likely fall early.

The system looks like a three-joint, one-legged hopper. If so, obs[2], obs[3] and obs[4] are the angles of joints 1 to 3, and obs[8], obs[9] and obs[10] are their speeds.

**How it works:**
- Each joint is driven back to angle 0 with a PD (spring and damper) controller. That freezes the body into a rigid, upright shape with the foot flat on the ground.
- This control is in joint coordinates, so I don't need to know the sign conventions for the body's world angles. A push on a joint moves that joint's angle in the same direction.
- In the upright pose the centre of mass sits above the ankle, which is inside the foot's footprint. Holding the ankle at angle 0 makes it work like a stiff ankle, which keeps the body's lean (obs[1]) near 0.
- The gains are kept moderate so the 0.008 s control step doesn't make the joints oscillate.

```python
import numpy as np

KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.08, 0.08, 0.05])
TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    a = KP * (TARGET - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```