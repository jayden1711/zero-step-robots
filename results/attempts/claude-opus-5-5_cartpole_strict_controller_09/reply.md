This looks like the classic inverted pendulum on a cart. I read the observation as `[cart position, pole angle, cart velocity, pole angular velocity]`, where `obs[1]` is the angle that ends the episode past 0.2 rad.

The controller is a linear state-feedback law:

- **Pole stabilisation (fast loop):** the cart is pushed toward the side the pole is leaning, using about 5.5 per radian of angle plus damping on the angular velocity.
- **Cart centring (slow loop):** a small extra term pulls the cart back toward the origin, so it doesn't drift into the rail limits over the 1000 steps (40 s). It has the same sign as the angle terms. That is correct for this kind of system: to move the cart left, you first push right so the pole tips left.

The gains come from a rough model: pole about 5 kg and 0.6 m long, cart about 10 kg, actuator gain about 100 N per unit of action. That gives a closed-loop angle response of roughly 8 rad/s, well within what a 0.04 s step can handle. The tiny initial errors stay far from the ±3 action limit.

Main risk: I couldn't test this, and the gains and sign convention rest on that assumed model. If the sign convention is the opposite of what I assumed, the controller will fail immediately.

```python
import numpy as np

# Linear state feedback for a cart-pole: obs = [x, theta, x_dot, theta_dot]
K_X = 0.1
K_THETA = 5.5
K_XDOT = 0.25
K_THETADOT = 0.9


def reset():
    pass


def act(obs):
    x, theta, xdot, thetadot = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, theta, xdot, thetadot])):
        return [0.0]
    u = K_X * x + K_THETA * theta + K_XDOT * xdot + K_THETADOT * thetadot
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
```