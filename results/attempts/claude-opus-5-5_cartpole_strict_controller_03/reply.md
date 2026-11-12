This looks like a cart-pole: `obs = [cart position, pole angle, cart velocity, pole angular velocity]`, with a force on the cart and termination when the pole angle exceeds 0.2 rad. The controller is a linear state-feedback (LQR-style) law. I placed the closed-loop poles from a rough linearised model:

- **Cart dynamics:** ẍ ≈ 6.5·u
- **Pole dynamics:** θ̈ ≈ 24.5·θ − 16·u
- **Pendulum modes:** a fast pair near −6 rad/s keeps the pole upright.
- **Cart modes:** a slow pair near −1 rad/s brings the cart back to centre.

All gains are positive. To return to centre, the cart first has to tilt the pole toward the centre. So the position and velocity terms have the same sign as the angle terms.

```python
import numpy as np

# State feedback: u = KX*x + KV*xdot + KT*theta + KW*thetadot
# obs = [cart position, pole angle, cart velocity, pole angular velocity]
KX = 0.23
KV = 0.53
KT = 5.4
KW = 1.1


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    u = KX * x + KV * xd + KT * th + KW * thd
    u = max(-3.0, min(3.0, u))
    return [u]
```