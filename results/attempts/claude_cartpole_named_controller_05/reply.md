I can't run anything here, so this is a hand-derived linear state-feedback controller and it is untested.

The gains come from a rough estimate of the model's dynamics. The motor gear is about 100, so one unit of action is about 100 N. The pole is about 5 kg and the cart about 10 kg. From that I estimate the pole's unstable rate at about 5 per second. A positive pole angle means the pole leans toward +x, so the controller pushes the cart toward +x. The cart position and velocity terms have the same sign, because bringing the cart back to centre means first leaning the pole the other way. They are kept small so the cart loop stays slower than the pole loop.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 4.0 * th + 0.3 * xd + 0.7 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
```

If the pole is slow to settle or the cart drifts, the first gains I'd tune are the cart terms (`0.1`, `0.3`).