This is a linear state-feedback (pole-placement) controller, designed from a linearised model of the MuJoCo `InvertedPendulum` system.

**Model.** I estimated the physical parameters from the standard model file:
- Cart mass is about 10.5 kg and pole mass about 5 kg.
- The pole's centre of mass is about 0.3 m above the hinge, and its inertia about the hinge is about 0.64 kg·m².
- The actuator gear is 100, so an action of u = 1 applies roughly 100 N.

Linearising with θ > 0 meaning the pole leans toward +x gives:

- θ̈ ≈ 32.7·θ − 22.2·u
- ẍ ≈ −3.3·θ + 8.9·u

**Gains.** With u = a·x + b·θ + c·ẋ + d·θ̇, the closed-loop characteristic polynomial is:

s⁴ + (22.2d − 8.9c)s³ + (22.2b − 8.9a − 32.7)s² + 217.7c·s + 217.7a

I placed the closed-loop poles as follows:
- The pole dynamics get a double pole at −6 rad/s. This is only slightly faster than the open-loop instability of about 5.7 rad/s, which keeps it robust to the 0.04 s zero-order hold and to errors in my parameter estimates.
- The cart dynamics get a slow double pole at −1.5 rad/s. This keeps the cart near 0 and well inside its ±1 m rail limit.

The resulting gains are a ≈ 0.37, b ≈ 4.97, c ≈ 0.62 and d ≈ 0.92, all positive. The commanded action stays far below the ±3 limit for the small perturbations involved.

```python
import numpy as np

# Linear state feedback u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement on a linearised cart-pole model of
# InvertedPendulum-v5 (cart ~10.5 kg, pole ~5 kg, gear 100):
#   pole dynamics: double pole at -6 rad/s
#   cart dynamics: double pole at -1.5 rad/s
K = np.array([0.372, 4.97, 0.62, 0.924])


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