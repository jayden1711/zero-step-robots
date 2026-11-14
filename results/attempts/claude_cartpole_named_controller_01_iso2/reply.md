This is a linear state-feedback controller. I couldn't run it, so the gains are estimated by hand, not tuned.

The pole angle is positive when it leans toward +x, so pushing the cart toward +x catches it. The cart position and velocity terms use the same sign. This is because, to bring the cart back, the pole must first lean toward the target, which means pushing away from it briefly. The gains are kept moderate so the 0.04 s step does not destabilize the loop.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 6.0 * th + 0.3 * v + 0.6 * w
    return [max(-3.0, min(3.0, u))]
```