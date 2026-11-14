This controller uses fixed state feedback, with gains from pole placement on a linearised model of the MuJoCo cart-pole.

**Model.** The values come from the `inverted_pendulum.xml` geometry: cart about 5.4 kg, pole about 4.9 kg with its centre of mass at 0.3 m, motor gear 100. A positive pole angle means the pole leans toward +x, so pushing the cart toward +x catches it. Linearised, this gives roughly:

- ẍ ≈ 15·u − 5.4·θ
- θ̈ ≈ 38·θ − 37.5·u

**Control law.** With u = a·x + b·ẋ + c·θ + d·θ̇, the closed-loop characteristic polynomial is:

s⁴ + (37.5d − 15b)s³ + (37.5c − 38 − 15a)s² + 367.5b·s + 367.5a

**Poles.** I placed the poles at (s+1.5)²(s+4)². They are kept moderate so the 0.04 s zero-order hold and modelling errors don't destabilise the loop. The small gains on x and ẋ keep the cart from drifting off the rail.

I haven't run this, so the score is untested.

```python
import numpy as np

# Gains from pole placement at (s+1.5)^2 (s+4)^2 on the linearised cart-pole:
#   x_dd  ~ 15 u - 5.4 theta
#   th_dd ~ 38 theta - 37.5 u
K_X = 0.098      # cart position
K_V = 0.18       # cart velocity
K_TH = 2.18      # pole angle
K_W = 0.365      # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    if not all(np.isfinite([x, th, v, w])):
        return [0.0]
    u = K_X * x + K_V * v + K_TH * th + K_W * w
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
```