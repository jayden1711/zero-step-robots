This is a linear state-feedback (LQR-style) controller, designed by pole placement on a linearised model of the cart-pole. I couldn't run it, so it is untested in the simulator.

**Model.** I estimated the model from the standard `InvertedPendulum` MuJoCo XML, recalled from memory rather than checked. The key values are:
- cart mass ≈ 10.5 kg
- pole mass ≈ 5 kg
- pole centre of mass about 0.3 m above the hinge
- motor gear 100, so 1 unit of action is about 100 N

The resulting linear dynamics are approximately:
- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ 8.51·u − 3.13·θ

**Gains.** With u = k₁x + k₂θ + k₃v + k₄ω, the closed-loop characteristic polynomial is:

s⁴ + (21.3k₄ − 8.51k₃)s³ + (21.3k₂ − 8.51k₁ − 32.3)s² + 208.2k₃·s + 208.2k₁

I placed the poles at {−3, −3, −8, −8}. That gives k₁ ≈ 2.77, k₂ ≈ 10.56, k₃ ≈ 2.54 and k₄ ≈ 2.05.

These poles are well within what the 0.04 s step can handle. The gains are moderate, so the action stays far from the ±3 clip for the tiny initial perturbations. All gains are positive. The cart-position terms have the same sign as the angle terms, which is the usual non-minimum-phase behaviour of a cart-pole. This keeps the cart from drifting along the rail while the pole stays upright.

```python
import numpy as np

# Linear state feedback: u = K . [x, theta, v, omega]
# Gains from pole placement at {-3, -3, -8, -8} on the linearised cart-pole model.
K = np.array([2.77, 10.56, 2.54, 2.05])


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