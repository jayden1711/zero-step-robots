This looks like a cart-pole: `obs = [cart position, pole angle, cart velocity, pole angular velocity]`, where the episode ends once the pole angle `obs[1]` exceeds 0.2 rad. The controller is linear state feedback, with gains set by pole placement on a linearised model.

**Model.** I estimated a cart of about 10.5 kg and a pole of about 5 kg and 0.6 m, with the input producing roughly 100 N per unit of action. Linearising gives:

- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ 8.51·u − 3.13·θ

**Closed loop.** With u = k₁x + k₂θ + k₃ẋ + k₄θ̇, the characteristic polynomial is:

s⁴ + (21.3k₄ − 8.51k₃)s³ + (21.3k₂ − 8.51k₁ − 32.3)s² + 208k₃·s + 208k₁

**Pole choice.** I placed the poles at −1.5, −1.5, −6 and −6. That is moderate bandwidth, so the loop should stay well damped with 0.04 s steps and tolerate errors in my model estimates.

**Signs.** All gains are positive, which matches the physics:

- A pole tilting toward +x is caught by pushing the cart toward +x.
- To bring the cart back to centre, the controller first nudges it outward so the pole leans the right way.

```python
import numpy as np

# Linear state feedback: u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement (poles at -1.5, -1.5, -6, -6) on a linearised cart-pole model.
K = np.array([0.389, 5.16, 0.648, 0.963])


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