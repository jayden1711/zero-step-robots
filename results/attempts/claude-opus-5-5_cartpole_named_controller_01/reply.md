This is a full-state linear feedback controller (pole placement) designed from a linearised model of the MuJoCo cart-pole.

**Model.** I estimated the physical parameters from the standard `inverted_pendulum.xml` geometry:

- Cart mass is about 10.5 kg and pole mass about 5 kg.
- The pole's centre of mass sits about 0.3 m above the hinge.
- The actuator gear is 100, so a control value `u` produces a force of 100·u N.

Linearising around upright gives:

- θ'' ≈ 32.3·θ − 21.3·u
- x'' ≈ 8.51·u − 3.13·θ

**Sign convention.** A positive angle means the pole leans toward +x, so the cart must push toward +x to catch it.

**Gains.** With `u = c·x + d·v + a·θ + b·ω`, the closed-loop characteristic polynomial is:

s⁴ + (21.3b − 8.51d)s³ + (21.3a − 32.3 − 8.51c)s² + 208.2d·s + 208.2c

I placed the poles as follows:

- A fast, well-damped pair (ω = 7 rad/s, ζ = 0.8) to balance the pole.
- A slow pair (ω = 1.5 rad/s, ζ = 0.9) to bring the cart back to the centre.

This gives c ≈ 0.53, d ≈ 0.76, a ≈ 5.55 and b ≈ 0.955. The initial perturbations are tiny, so the ±3 limit on the action should not be reached during normal operation.

```python
import numpy as np

# Linear state feedback: u = c*x + d*v + a*theta + b*omega
# Gains from pole placement on a linearised cart-pole model
# (fast pair: wn=7, zeta=0.8; slow pair: wn=1.5, zeta=0.9).
K_X = 0.53
K_V = 0.756
K_TH = 5.55
K_OM = 0.955


def reset():
    pass


def act(obs):
    x, th, v, om = (float(o) for o in obs[:4])
    u = K_X * x + K_V * v + K_TH * th + K_OM * om
    if not np.isfinite(u):
        u = 0.0
    u = max(-3.0, min(3.0, u))
    return [u]
```