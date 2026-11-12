This is a linear state-feedback (LQR-style, pole-placement) controller. I couldn't run it, so the gains are derived from estimates, not tested.

**Model.** I estimated the physical parameters from the standard `inverted_pendulum.xml`, using MuJoCo's default density of 1000 kg/m³:

- Cart mass ≈ 10.5 kg.
- Pole mass ≈ 5 kg, centre of mass 0.3 m above the hinge.
- Pole inertia about the hinge ≈ 0.6 kg·m².
- Actuator gear = 100, so the force on the cart is 100·u.

Linearising, with positive angle meaning the pole tilts toward +x, gives:

- ẍ ≈ 8.51·u − 3.13·θ
- θ̈ ≈ 32.3·θ − 21.28·u

**Gains.** With u = kx·x + kθ·θ + kv·ẋ + kω·θ̇, the closed-loop characteristic polynomial is:

s⁴ + (21.28kω − 8.51kv)s³ + (21.28kθ − 8.51kx − 32.3)s² + 208.3kv·s + 208.3kx

I placed the poles at {−3, −3, −8, −8}, which gives kx ≈ 2.77, kθ ≈ 10.57, kv ≈ 2.54, kω ≈ 2.05.

- **Step size:** the fastest pole (−8) times the 0.04 s step is about 0.32, comfortably slow enough for the discrete steps.
- **Actuator limits:** the commands stay far below the ±3 limit for the tiny initial perturbations.
- **Damping:** the joint damping in the model only adds extra stability.
- **Signs:** all gains are positive. Pushing toward the side the pole leans keeps it upright. The positive cart-position gain gives the correct "push away first" behaviour that brings the cart back to centre.

```python
import numpy as np

# State feedback gains from pole placement on the linearised cart-pole model
# (closed-loop poles at -3, -3, -8, -8).
K = np.array([2.77, 10.57, 2.54, 2.05])  # [x, theta, x_dot, theta_dot]


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