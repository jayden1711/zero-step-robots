This assumes the system is a cart-pole balancing task (MuJoCo InvertedPendulum style), with obs = [cart x, pole angle, cart velocity, angular velocity]. The controller is a linear state feedback. I could not run it, so the gains come from a rough stability estimate.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs[0], obs[1], obs[2], obs[3]
    u = 0.1 * x + 2.5 * th + 0.2 * xd + 0.4 * thd
    return [max(-3.0, min(3.0, u))]
```

The angle and angular-velocity terms keep the pole upright. The small cart position and velocity terms (same sign, as in the standard cart-pole LQR solution) keep the cart from drifting off. The gains are kept moderate because the 0.04 s step makes high gains unstable.