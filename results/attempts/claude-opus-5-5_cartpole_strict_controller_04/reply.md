This looks like a cart-pole (inverted pendulum on a cart). I'm assuming:

- `obs = [cart position, pole angle, cart velocity, pole angular velocity]`
- positive action pushes the cart in +x
- a positive pole angle means the pole leans toward +x

**How the gains were derived.** I estimated the cart and pole masses and inertia for this kind of model: gear about 100, pole about 5 kg with its centre of mass about 0.3 m up, cart about 10.5 kg. Linearising about upright gives roughly:

- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ −3.13·θ + 8.51·u

The combination y = 21.3·x + 8.51·θ is a flat output, with ÿ ≈ 208·θ. That makes exact pole placement simple. I placed all four closed-loop poles at s = −4. This is well within what a 0.04 s step can handle, and it keeps the actions small and far from the ±3 limit. The result is a full-state feedback law:

u = 1.23·x + 6.52·θ + 1.23·ẋ + 1.24·θ̇

The positive cart-position gain is the usual non-minimum-phase behaviour: to bring the cart back, the controller first pushes it the "wrong" way so the pole tips toward the origin. I couldn't run this, so the gains rest on these estimates and haven't been tested.

```python
import numpy as np

# Full-state feedback (pole placement, all closed-loop poles at s = -4)
# state: [cart pos, pole angle, cart vel, pole angular vel]
K = np.array([1.23, 6.52, 1.23, 1.24])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
```