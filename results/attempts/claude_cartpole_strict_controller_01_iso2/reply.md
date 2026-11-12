This looks like the MuJoCo inverted pendulum, with obs as [cart position, pole angle, cart velocity, pole angular velocity]. I wrote a linear state-feedback controller on that assumption. I could not run it, so the gains are estimates and untested.

The pole angle and angular velocity terms push the cart toward the lean. The small position and velocity terms with the same sign keep the cart from drifting away.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 5.0 * th + 0.25 * v + 0.7 * w
    return [max(-3.0, min(3.0, u))]
```