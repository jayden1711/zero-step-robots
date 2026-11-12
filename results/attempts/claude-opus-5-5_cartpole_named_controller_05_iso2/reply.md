This is a linear state-feedback (pole-placement) controller, derived from an approximate model of the MuJoCo `InvertedPendulum-v5` system. I couldn't run it, so it is untested.

**Model behind the gains**
- I estimated the masses from the model geometry: cart ≈ 5.4 kg, pole ≈ 5 kg, centre of mass 0.3 m up the pole. The actuator gear is 100.
- Linearised, this gives:
  - θ̈ ≈ 38.3·θ − 37.6·u
  - ẍ ≈ 15·u − 5.5·θ
- A positive angle means the pole leans toward +x, so the controller pushes the cart toward +x to catch it.

**Gains**
- I placed the closed-loop poles at −4, −4, −6, −6 rad/s. These are slow compared with the 0.04 s control step, which gives some margin for model error.
- Solving for those poles gives u = 1.567·x + 5.58·θ + 1.305·v + 1.053·ω.
- The small position and velocity terms stop the cart drifting along the rail.
- The output is clipped to [−3, 3]. With initial perturbations of at most 0.01, the controller should stay well inside that range.

```python
import numpy as np

# Linear state feedback u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement (poles at -4, -4, -6, -6) on a linearised
# model of the MuJoCo InvertedPendulum (gear 100).
K = np.array([1.567, 5.58, 1.305, 1.053])


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