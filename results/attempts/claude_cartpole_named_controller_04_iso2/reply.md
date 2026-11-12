This is a linear state-feedback controller. I couldn't run it, so the gains are hand-estimated from rough cart-pole dynamics and untested.

In this environment a positive angle means the pole leans toward +x, and a positive action pushes the cart toward +x. So the angle and angular-velocity gains are positive to catch the pole. The cart position and velocity gains are also small and positive, which is the usual sign for a cart-pole. That slowly steers the cart back toward the centre by first tilting the pole the right way.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.05 * x + 3.0 * th + 0.15 * v + 0.5 * w
    return [max(-3.0, min(3.0, u))]
```