This is a balance-only controller. The scoring makes "stay healthy for all 1000 steps" worth about 1000 points, and I can't test anything. So I chose a conservative standing controller over a hand-tuned hopping gait, which would likely fall early and score less.

**How it works:**
- I read the observation as a planar one-legged hopper:
  - obs[0] is torso height and obs[1] is torso pitch.
  - obs[2:5] are the three joint angles and obs[8:11] are their velocities.
  - obs[5:8] are the torso's forward speed, vertical speed and pitch rate.
- With all three joints held near zero, the body is an upright rigid stick. Its centre of mass sits above the ankle, inside the foot's contact span, so it should be statically stable.
- A PD controller holds each joint at its target. The gains are kept moderate because each action is held for 8 ms, and high damping gains would become unstable.
- A small extra term adjusts the hip and ankle targets to push torso pitch back toward 0. I'm not certain of the sign convention, so I kept this term weak and capped it. If the sign is wrong, the stiff joint hold should still dominate.
- The control cost is negligible: actions stay small, so 0.001·Σa² is tiny.

The expected score is about 1000 if it stays upright for every episode. This is untested, so I can't confirm it.

```python
import numpy as np

KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.1, 0.1, 0.08])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    pitch_rate = o[7]
    q = o[2:5]
    qd = o[8:11]

    # weak, bounded torso-upright correction applied through joint targets
    corr = float(np.clip(0.3 * pitch + 0.02 * pitch_rate, -0.05, 0.05))
    target = np.array([corr, 0.0, -corr])

    a = KP * (target - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```