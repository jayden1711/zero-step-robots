This looks like a cart-pole balancing task: obs[1] is the pole angle, with a 0.2 rad failure threshold. I assume the observation is `[cart position, pole angle, cart velocity, pole angular velocity]` and that positive action pushes the cart toward +x. This matches the standard MuJoCo inverted pendulum. I haven't run this, so the gains are untested.

The controller is a linear state-feedback law:

- **Fast inner loop on the pole.** Strong proportional-derivative feedback on angle and angular rate keeps the pole upright, aiming for about 8 rad/s bandwidth, well damped.
- **Slow outer loop on the cart.** Small positive gains on cart position and velocity bring the cart back toward the centre. The positive sign is deliberate: it makes the pole lean toward the centre, which then drives the cart there.

A rough linearised model gave pole dynamics of about θ̈ ≈ 32θ − 21u and cart dynamics of about ẍ ≈ 8.5u − 3θ. From these, the gains are kθ≈4.5, kω≈0.6, kx≈0.25 and kv≈0.5. They keep enough stability margin at the 0.04 s step.

```python
import numpy as np

K_X = 0.25      # cart position
K_TH = 4.5      # pole angle
K_V = 0.5       # cart velocity
K_W = 0.6       # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    if not all(np.isfinite([x, th, v, w])):
        return [0.0]
    u = K_X * x + K_TH * th + K_V * v + K_W * w
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
```