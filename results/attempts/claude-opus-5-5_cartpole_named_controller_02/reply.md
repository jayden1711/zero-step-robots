The controller below is a linear state-feedback (PD-style) balancer. I couldn't run it, so the gains come from a rough linearised model and are untested.

**How I chose the gains:**
- **Masses from the model.** The rail actuator has gear 100, so each action unit is 100 N. At density 1000, the cart is about 10.5 kg and the pole about 5 kg (0.6 m long). The pole's effective length is about 0.4 m.
- **Pole loop.** With `u = 3·θ + 0.3·θ̇`, the linearised pole loop has a natural frequency of about 5 rad/s with damping ratio about 0.5. Over a 0.04 s step that is ω·dt ≈ 0.2, so the coarse step should not cause instability.
- **Cart loop.** The cart position and velocity gains are small and positive (0.1 and 0.2). A cart that has drifted to +x first has to push +x so the pole leans back toward the centre, then move toward it. This outer loop settles slowly (about 0.8 rad/s) and keeps the cart near the middle of the rail for the full 1000 steps.
- **Sign assumption.** The hinge rotates about +y, so a positive angle should mean the pole leans toward +x. That means positive angle and angular velocity call for positive force. This is the assumption the controller depends on most.

```python
import numpy as np


def reset():
    pass


def act(obs):
    x, theta, x_dot, theta_dot = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, theta, x_dot, theta_dot])):
        return [0.0]
    u = 0.1 * x + 3.0 * theta + 0.2 * x_dot + 0.3 * theta_dot
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
```