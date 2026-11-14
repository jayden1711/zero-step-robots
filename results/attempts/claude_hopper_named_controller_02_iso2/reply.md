This is an untested, hand-designed standing controller. It holds the hip and knee straight with PD control and balances the torso with ankle torque, aiming for the roughly 1000 survival reward and giving up forward speed. The ankle sign (positive foot torque pushes the torso backward) comes from reasoning about the joint axes, and I couldn't verify it in simulation.

```python
import numpy as np

def reset():
    pass

def act(obs):
    z, ang, q1, q2, q3, vx, vz, w, d1, d2, d3 = obs
    a1 = -3.0 * q1 - 0.1 * d1
    a2 = -3.0 * q2 - 0.1 * d2
    a3 = 4.0 * ang + 0.5 * w + 0.2 * vx
    a = [a1, a2, a3]
    return [float(np.clip(x, -1.0, 1.0)) for x in a]
```