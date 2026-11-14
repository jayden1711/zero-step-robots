This is a standing-balance controller. It does not try to hop. A healthy step is worth +1 and there are 1000 of them, so staying upright for the whole episode scores about 1000. A forward gait might score more, but tuned blind it is far more likely to fall early. That makes balance the safer bet. I could not run or test it, so the gains are estimated rather than tuned.

The observation layout looks like a one-legged planar hopper:

| Index | Meaning |
|---|---|
| 0 | height |
| 1 | torso pitch |
| 2–4 | hip, knee and ankle angles |
| 5 | forward velocity |
| 6 | vertical velocity |
| 7 | torso pitch rate |
| 8–10 | joint velocities |

The controller has three parts:

- **Knee:** held straight with a small push into its straight-leg limit.
- **Hip:** a PD loop keeps the torso upright.
- **Ankle:** a PD loop keeps the leg's lean slightly forward, over the forward-extending foot. It also leans back a little if the body starts drifting forward. Ankle torque is kept small so the foot does not roll onto its toe or heel.

```python
import numpy as np


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    th = o[1]                       # torso pitch (+ = leaning forward)
    qt, ql, qf = o[2], o[3], o[4]   # hip, knee, ankle angles
    vx = o[5]
    thd = o[7]
    qtd, qld, qfd = o[8], o[9], o[10]

    # Hip: keep the torso upright.
    a_hip = -1.0 * th - 0.10 * thd

    # Knee: keep the leg straight (pressed gently into its limit).
    a_knee = 0.3 + 3.0 * (0.0 - ql) - 0.10 * qld

    # Ankle: whole-body balance. Leg absolute pitch = torso - hip - knee.
    phi = th - qt - ql
    phid = thd - qtd - qld
    phi_ref = 0.03 - 0.05 * np.clip(vx, -1.0, 1.0)
    a_foot = 1.0 * (phi_ref - phi) - 0.30 * phid
    # Keep ankle torque small so the foot stays flat on the ground.
    a_foot = float(np.clip(a_foot, -0.15, 0.15))

    a = np.clip([a_hip, a_knee, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```