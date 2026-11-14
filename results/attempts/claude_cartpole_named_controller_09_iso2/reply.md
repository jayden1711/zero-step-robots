This is a linear state-feedback controller. I haven't run it, and the gains come from a rough dynamics estimate rather than tuning.

The pole angle is positive when it leans toward +x, so pushing the cart in the same direction as the lean catches it. The cart-position and cart-velocity terms use the same sign, with small gains. That is the standard non-minimum-phase LQR pattern, and it keeps the cart from drifting into the rail limits.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 5.0 * th + 0.3 * xd + 0.6 * thd
    return [max(-3.0, min(3.0, u))]
```