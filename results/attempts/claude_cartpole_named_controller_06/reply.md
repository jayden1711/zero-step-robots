I couldn't run or test this, so the gains below are hand-derived from my rough estimate of the model's dynamics and are untested.

It is a linear state-feedback controller. The pole angle is positive when the pole leans toward +x, so pushing the cart in that direction catches it. The cart position and velocity terms are small and have the same sign, which slowly pulls the cart back toward the centre. The output is clipped to [-3, 3].

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 0.3 * xd + 3.5 * th + 0.5 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
```