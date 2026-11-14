This looks like a cart-pole balancing task. My reading of the observation is cart position, pole angle, cart velocity and pole angular velocity, which matches the MuJoCo InvertedPendulum layout. I couldn't run anything, so the controller below is untested.

The controller is a fixed linear rule. It pushes the cart toward the side the pole leans, with a damping term on the pole's spin. Small position and velocity terms slowly bring the cart back to the centre.

**Biggest assumption:** I assumed a positive angle means the pole leans toward the side a positive action pushes. If that's backwards, every episode will fail in the first few steps.

I estimated the dynamics as follows:
- Pole: about 5 kg, centre of mass 0.3 m up.
- Cart: about 10 kg.
- Force: about 100 N per unit of action.

With those numbers, the balance loop settles in a fraction of a second. The cart-centring loop is much slower, with a period of about 10 seconds. The gains should keep the action within ±3 for any angle up to the 0.2 limit.

```python
import numpy as np

K_THETA = 5.0
K_OMEGA = 0.6
K_X = 0.1
K_V = 0.2


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    u = K_THETA * th + K_OMEGA * w + K_X * x + K_V * v
    if not np.isfinite(u):
        u = 0.0
    return [float(np.clip(u, -3.0, 3.0))]
```