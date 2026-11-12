I can't run anything, so I aimed for something likely to work rather than something fast. The controller just balances the hopper standing upright. That should earn about 1 per step for 1000 steps, so roughly 1000, as long as my reading of the joint signs is right. I didn't try a hopping gait, which scores much higher, because it is too risky to tune blind.

The design treats each action as one joint, assuming the standard 2D hopper layout:
- **Action 0, hip:** holds the torso upright, using `obs[1]` and `obs[7]`.
- **Action 1, knee:** holds the knee straight, using `obs[3]` and `obs[9]`.
- **Action 2, ankle:** balances the whole leg over the foot. It is clipped to a small torque so the foot doesn't tip onto its heel or toe.

If any of those signs is backwards, the hopper will fall early and the score will be much lower.

```python
import numpy as np

_integ = 0.0


def reset():
    global _integ
    _integ = 0.0


def act(obs):
    global _integ
    o = np.asarray(obs, dtype=float)
    th, qt, qk, qf = o[1], o[2], o[3], o[4]
    thd, qtd, qkd, qfd = o[7], o[8], o[9], o[10]

    # Hip: keep torso upright (reaction torque on torso is +u about +y)
    u_hip = -1.5 * th - 0.1 * thd

    # Knee: keep straight
    u_knee = 2.0 * (0.0 - qk) - 0.1 * qkd + 0.05

    # Ankle: keep leg lean over foot near small forward target
    phi = th - qt - qk
    phid = thd - qtd - qkd
    err = phi - 0.02
    _integ = float(np.clip(_integ + err * 0.008, -0.2, 0.2))
    u_ank = -0.8 * err - 0.15 * phid - 0.3 * _integ
    u_ank = float(np.clip(u_ank, -0.1, 0.1))

    return [float(np.clip(u_hip, -1, 1)),
            float(np.clip(u_knee, -1, 1)),
            u_ank]
```