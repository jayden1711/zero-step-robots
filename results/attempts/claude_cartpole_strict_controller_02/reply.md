This controller is untested, as the task requires. It is a linear state-feedback law, and its gains and the signs on the cart terms are estimated by hand, not tuned. I assumed this is a MuJoCo cart-pole with `obs = [cart pos, pole angle, cart vel, pole angular vel]`, and that a positive push moves the cart toward the side the pole leans.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs[0], obs[1], obs[2], obs[3]
    a = 0.1 * x + 3.0 * th + 0.3 * v + 0.45 * w
    if a > 3.0:
        a = 3.0
    elif a < -3.0:
        a = -3.0
    return [a]
```