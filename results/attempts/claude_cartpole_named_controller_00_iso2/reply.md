This is a linear state-feedback controller, `u = kx·x + kθ·θ + kv·ẋ + kω·ω`. I couldn't run it, so the gains come from a rough hand estimate and are untested. All four gains are positive, because a positive pole angle leans toward +x and the cart should be pushed that way.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 3.0 * th + 0.3 * xd + 0.4 * thd
    return [max(-3.0, min(3.0, u))]
```