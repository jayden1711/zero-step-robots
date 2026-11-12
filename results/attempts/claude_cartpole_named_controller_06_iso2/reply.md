This is an untested linear state-feedback controller, `u = kx·x + kθ·θ + kv·v + kω·ω`, with gains chosen from rough physical estimates. All four gains are positive, because pushing the cart toward the side the pole leans corrects the lean. The cart position and velocity terms are small and only keep the cart from drifting off the rail.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 3.0 * th + 0.3 * v + 0.4 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
```

I couldn't run the simulation, so the gains are estimates and may need tuning if the score is low.