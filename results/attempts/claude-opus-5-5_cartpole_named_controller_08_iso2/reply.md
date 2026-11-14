This is a linear state-feedback (pole-placement) controller, derived from a linearized model of the MuJoCo `InvertedPendulum-v5` cart-pole. I haven't run it, so the score is untested.

**Model.** I estimated the physical parameters from the environment's model file:
- Cart mass is about 10.5 kg and pole mass is about 5 kg.
- The pole is 0.6 m long, with its centre of mass about 0.3 m above the hinge.
- The actuator gear is 100, so the cart force is 100 × action.

Linearizing around upright gives these equations:
- cart acceleration ≈ 8.51·a − 3.13·θ
- pole angular acceleration ≈ 32.3·θ − 21.3·a

A positive angle means the pole leans toward +x. Pushing the cart in the +x direction corrects that lean, so all four feedback gains are positive.

**Gain design.** With `a = k1·x + k2·v + k3·θ + k4·ω`, the closed-loop characteristic polynomial is:

s⁴ + (21.3k4 − 8.51k2)s³ + (21.3k3 − 8.51k1 − 32.3)s² + 208.3k2·s + 208.3k1

I placed all four poles at s = −4. That is fast enough to correct quickly, but slow compared with the 0.04 s step (λ·dt = 0.16), so the time steps shouldn't destabilize it. It also leaves some margin if my mass estimates are off. The resulting gains are:
- k1 = k2 ≈ 1.23 (cart position and velocity)
- k3 ≈ 6.5 (pole angle)
- k4 ≈ 1.24 (pole angular velocity)

With the initial perturbations of at most 0.01, the actions stay well inside the ±3 limit. The cart is also driven back toward the centre of the rail.

```python
import numpy as np

# Linear state feedback from pole placement (all closed-loop poles at s = -4)
# on the linearized cart-pole model of InvertedPendulum-v5.
K_X = 1.229      # cart position
K_V = 1.229      # cart velocity
K_TH = 6.515     # pole angle
K_OM = 1.242     # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, om = (float(o) for o in obs)
    a = K_X * x + K_V * v + K_TH * th + K_OM * om
    if not np.isfinite(a):
        a = 0.0
    a = float(np.clip(a, -3.0, 3.0))
    return [a]
```