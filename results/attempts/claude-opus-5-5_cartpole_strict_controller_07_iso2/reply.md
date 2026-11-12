This looks like a classic cart-pole: `obs = [cart_pos, pole_angle, cart_vel, pole_ang_vel]`, with a force-like action. I estimated gains from a rough physical model, since I couldn't run anything:

- **Pole loop:** strong proportional-derivative feedback on the pole angle. A positive tilt gets a positive push so the cart moves under the pole.
- **Cart loop:** weak feedback on cart position and velocity. Its sign is chosen so the cart drifts back toward the centre by gently tilting the pole first.

```python
import numpy as np

# Gains: [cart_pos, pole_angle, cart_vel, pole_ang_vel]
K = np.array([0.15, 5.0, 0.3, 0.8])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    a = float(np.dot(K, o))
    a = max(-3.0, min(3.0, a))
    return [a]
```