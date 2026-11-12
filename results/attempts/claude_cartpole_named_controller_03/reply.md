I can't run anything here, so this is an untested hand-tuned state-feedback (LQR-style) controller. The gains are my estimates from the model's approximate masses and pole length, not tuned values.

Positive pole angle means the pole leans toward +x, so the cart is pushed the same way. The cart-position and velocity terms also have positive sign, as in standard LQR for this system. They make the cart lean the pole back toward the centre, and the gains on them are small.

```python
def reset():
    pass


def act(obs):
    x, theta, v, w = obs
    u = 0.1 * x + 0.3 * v + 6.0 * theta + 0.8 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
```