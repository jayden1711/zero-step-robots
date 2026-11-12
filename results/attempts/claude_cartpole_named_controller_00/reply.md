This is an untested linear state-feedback controller. I couldn't run it, and its gains come from a rough hand model of the cart and pole, not from the simulator itself.

- **Pole loop:** push the cart toward the side the pole leans, using the pole angle and angular velocity. This is the fast loop.
- **Cart loop:** small gains on cart position and velocity, with the same sign as the pole terms. This is the standard fix for a cart that has to lean the pole before it can move back. The gains are small enough that this loop stays much slower than the pole loop, so it keeps the cart near the centre of the rail without upsetting balance.
- **Sign convention:** my model assumed a positive angle means the pole tips toward +x. If the simulator uses the opposite convention, the pole terms would have the wrong sign and the controller would fail.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 3.0 * th + 0.45 * thd + 0.1 * x + 0.25 * xd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
```