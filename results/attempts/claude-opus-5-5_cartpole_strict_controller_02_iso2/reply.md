This looks like a cart-pole balance task (most likely MuJoCo `InvertedPendulum`). I've assumed `obs = [cart position, pole angle, cart velocity, pole angular velocity]`, and that a positive action pushes the cart toward +x. The pole angle is obs[1], the value that ends the episode.

The controller is a linear state-feedback law, designed using a rough linearised model of the system:

- **Pole loop:** strong proportional and damping gains on the angle and angular rate. A positive angle means the pole leans toward +x, so the cart is pushed toward +x to catch it.
- **Cart loop:** weak positive gains on cart position and velocity. These slowly bring the cart back to the centre so it doesn't drift into the rail limits over 1000 steps. The sign is positive because the cart first has to move slightly further out to tip the pole back toward the centre.

```python
import numpy as np

# Linear state-feedback gains: [cart pos, pole angle, cart vel, pole ang vel]
K = np.array([0.3, 5.0, 0.5, 1.0])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
```