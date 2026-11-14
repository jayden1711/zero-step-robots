This uses a linear state-feedback (pole-placement) controller built from a linearised model of the MuJoCo cart-pole. I couldn't run it, so these values are estimates, not tested results.

**Model assumptions** (taken from the standard `inverted_pendulum.xml` with default density 1000):
- Cart mass about 10.5 kg; pole about 5 kg, 0.6 m long, centre of mass 0.3 m above the hinge.
- The actuator gear is 100, so an action of `u` gives a force of `100·u` N.
- A positive pole angle means the pole leans toward +x. The hinge axis is +y, so to catch the pole the cart has to be pushed toward +x.

**Linearised dynamics**
- (M+m)·ẍ + m·l·θ̈ = F
- m·l·ẍ + I·θ̈ = m·g·l·θ

Solving these gives ẍ = (F − 36.75·θ) / 11.75 and θ̈ = 24.5·θ − 2.5·ẍ.

**Gain design**
- I commanded a cart acceleration `a` and placed all four closed-loop poles at s = −4 rad/s.
- That gives a = 10.45·x + 52.4·θ + 10.45·ẋ + 10.58·θ̇.
- Mapped back to force and divided by the gear: u ≈ 1.23·x + 6.52·θ + 1.23·ẋ + 1.24·θ̇.

**Why these values**
- With |θ| ≤ 0.01 at the start, the action is tiny, so the output never saturates.
- A bandwidth of 4 rad/s is slow compared with the 0.04 s step, so discretisation has little effect.
- The design should tolerate moderate errors in the mass estimates and the joint damping.

```python
import numpy as np

# Linear state feedback: u = K . [x, theta, x_dot, theta_dot]
# Derived by pole placement (all poles at -4 rad/s) on the linearised cart-pole
# model of InvertedPendulum (cart ~10.5 kg, pole ~5 kg, gear 100).
K = np.array([1.228, 6.52, 1.228, 1.243])


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