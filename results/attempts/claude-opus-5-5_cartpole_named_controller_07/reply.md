This is a fixed linear state-feedback (LQR-style) controller. I designed the gains by hand from an approximate model of the MuJoCo cart-pole. I couldn't run it, so the score is untested.

```python
import numpy as np

# Linear state feedback: u = Kx*x + Kv*v + Kth*theta + Kw*omega
# Positive pole angle leans toward +x, so all gains are positive
# (push the cart under the falling pole; position terms are the slow outer loop).
K_X = 0.3
K_V = 0.5
K_TH = 6.0
K_W = 0.8


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    u = K_X * x + K_V * v + K_TH * th + K_W * w
    if not np.isfinite(u):
        u = 0.0
    return [float(np.clip(u, -3.0, 3.0))]
```

**How I chose the gains**

- **Model.** The motor gear is about 100, the cart is about 17 kg and the pole about 5 kg, with the pole 0.6 m long. From this I estimated two linearised equations:
  - pole: θ'' ≈ 24.5·θ − 12.5·u
  - cart: x'' ≈ 5·u
- **Pole (fast loop).** The angle gain of 6 and angular-velocity gain of 0.8 give a well-damped loop at roughly 7–8 rad/s. That is well within what the 0.04 s step can handle. The angle gain is about 3× the minimum needed for stability (about 2), so it should tolerate model errors of about 2×.
- **Cart position (slow loop).** The position gain of 0.3 and velocity gain of 0.5 give a slow loop at about 0.9 rad/s with damping ratio about 0.7. This keeps the cart near the centre of the rail without disturbing the pole loop.
- **Saturation.** At the termination angle of 0.2 rad, the angle term asks for 1.2, well inside the ±3 limit, so the force rarely saturates.