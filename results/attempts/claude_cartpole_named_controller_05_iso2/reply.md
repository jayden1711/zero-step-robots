I couldn't run or test this, so the gains below are a reasoned guess rather than a tuned result. The controller is a linear state-feedback law. A positive pole angle means the pole leans toward +x, so the cart is pushed the same way to catch it. The cart position and velocity gains also take that sign, which is the usual LQR result for a cart-pole. The gains are moderate, because the actuator is strong and the 0.04 s step makes high gains risky.

```python
def reset():
    pass

def act(obs):
    x, th, xd, thd = obs
    u = 0.5 * x + 8.0 * th + 0.6 * xd + 1.5 * thd
    return [max(-3.0, min(3.0, u))]
```