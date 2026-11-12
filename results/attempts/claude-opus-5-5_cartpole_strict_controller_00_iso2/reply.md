This looks like a cart-pole (inverted pendulum on a cart). I'm assuming the observation is [cart position, pole angle, cart velocity, pole angular velocity], with positive force pushing the cart in the direction the pole leans. None of this is tested; it rests on that assumption.

The controller is a full-state linear feedback law:
- **Angle and angular velocity:** strong PD gains keep the pole upright.
- **Cart position and velocity:** small gains slowly pull the cart back toward the origin. Their sign matches the standard LQR solution, where the cart terms have the same sign as the angle terms. This stops the cart from drifting over 1000 steps.

```python
import numpy as np

# obs = [cart_pos, pole_angle, cart_vel, pole_ang_vel]
K_X = 0.1
K_TH = 5.0
K_XD = 0.3
K_THD = 0.5


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    u = K_X * x + K_TH * th + K_XD * xd + K_THD * thd
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
```