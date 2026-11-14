This is a linear state-feedback controller. I couldn't run it, so the gains are estimated by hand and untested.

The reasoning behind them:
- The pole leans toward +x at positive angles, so the force on the cart pushes the same way as the lean.
- The cart position and velocity terms take the same sign as the angle terms, as in the standard cart-pole LQR solution. They are kept small so they only gently pull the cart back toward the centre.
- A rough model of the actuator gain and pole length puts the closed-loop pole angle dynamics at a natural frequency of about 7 rad/s with good damping. That is comfortably stable at a 0.04 s step.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 4.0 * th + 0.3 * v + 0.5 * w
    return [max(-3.0, min(3.0, u))]
```