This looks like the MuJoCo inverted-pendulum (cart-pole) task, with observations `[cart x, pole angle, cart velocity, angle velocity]`. I wrote a linear state-feedback balancer on that assumption. I couldn't run it, so the gains are untested estimates.

```python
def reset():
    pass

def act(obs):
    x, th, xd, thd = obs
    u = 0.3 * x + 6.0 * th + 0.5 * xd + 0.8 * thd
    return [max(-3.0, min(3.0, u))]
```

Positive angle is assumed to mean the pole leans toward +x, so a positive action pushes the cart under the pole. The cart position and velocity terms also carry a positive sign, which is the standard LQR sign for a cart-pole. If the sign assumption is wrong the controller will fail immediately.