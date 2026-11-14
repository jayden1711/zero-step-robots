This looks like a cart-pole: obs is probably [cart position, pole angle, cart velocity, pole angular velocity], and the action is a force on the cart. I wrote a linear state-feedback controller with gains from a rough linearized model. I couldn't run or tune it here.

- **Angle loop:** the angle and angular-velocity gains (about 8 and 1.2) aim to make the pole settle quickly, at about 8 rad/s and close to critically damped.
- **Position loop:** small position and velocity gains have the same sign as the angle gains. In this kind of system that sign keeps the cart from slowly drifting away, because the cart has to lean the pole first to move.

The main risk is the sign convention. If a positive pole angle does not mean the pole tilts toward the positive cart direction, every gain has the wrong sign and the controller will fail at once.

```python
import numpy as np

K_X = 0.2      # cart position
K_TH = 8.0     # pole angle
K_V = 0.4      # cart velocity
K_W = 1.2      # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    u = K_X * x + K_TH * th + K_V * v + K_W * w
    if not np.isfinite(u):
        u = 0.0
    return [float(np.clip(u, -3.0, 3.0))]
```