This is a guess at the system, since I can't run anything. I'm treating it as a cart-pole (obs = cart position, pole angle, cart velocity, pole angular velocity), where pushing the cart toward the lean direction rebalances the pole. The controller is a linear state-feedback law with all-positive gains. The gains are hand-picked and untested.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.2 * x + 8.0 * th + 0.5 * xd + 1.5 * thd
    return [max(-3.0, min(3.0, u))]
```