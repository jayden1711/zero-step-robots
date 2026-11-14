Linear state-feedback controller, derived from a linearised model of the MuJoCo cart-pole. The model uses pole ≈ 5 kg, centre of mass at 0.3 m, cart ≈ 10 kg, and actuator gear 100, so each unit of action is about 100 N.

- **Pole loop:** the inner gains set this loop to about 8 rad/s with roughly 0.75 damping. That is well within what a 0.04 s control step can handle.
- **Cart loop:** a slow outer loop (about 0.8 rad/s) keeps the cart from drifting along the rail over the 1000 steps.
- **Gain signs:** all four gains are positive. A positive hinge angle tilts the pole toward +x, so the cart must be pushed toward +x to catch it. To return the cart to centre, the controller first pushes the cart further out, which makes the pole lean back toward the centre.

I couldn't run this, so these gains are hand-derived and untested.

```python
import numpy as np

# State feedback gains: [cart pos, pole angle, cart vel, pole ang vel]
K = np.array([0.2, 4.7, 0.35, 0.63])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
```