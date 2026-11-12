This is my best guess, untested. I assumed `obs` is `[cart position, pole angle, cart velocity, pole angular velocity]`, as in the MuJoCo InvertedPendulum task, and that a positive angle means the pole leans toward +x. The controller is a linear state-feedback law, and the cart-position and cart-velocity terms have the same sign as the angle term, as in the standard LQR solution for this system. The gains are estimates, not tuned.

```python
import numpy as np

def act(obs):
    x, th, xd, thd = obs
    u = 0.3 * x + 8.0 * th + 0.5 * xd + 1.0 * thd
    return [float(np.clip(u, -3.0, 3.0))]
```