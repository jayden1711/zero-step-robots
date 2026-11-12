This looks like a cart-pole: obs[1] is the pole angle, which must stay within ±0.2. I assumed the ordering `[cart position, pole angle, cart velocity, pole angular velocity]`, with the same sign convention for force and angle.

The controller is a linear state feedback. I placed the poles for an approximate linearised model of a heavy cart and pole driven by a strong actuator. I then checked with the Routh–Hurwitz criterion that the closed loop stays stable across a wide range of plausible cart and pole masses. Every gain is positive:

- If the pole tilts toward +x, the cart pushes toward +x to get back under it.
- The position and velocity terms bring the cart back toward the centre without letting the pole fall.

I could not run this, so it is untested.

```python
import numpy as np

# Linear state feedback: u = K . [x, theta, x_dot, theta_dot]
# Gains chosen by pole placement on a linearised cart-pole model and checked
# (Routh-Hurwitz) to remain stable across a wide range of mass/inertia guesses.
K = np.array([2.0, 7.5, 1.8, 1.4])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if s.shape[0] < 4 or not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s[:4]))
    u = max(-3.0, min(3.0, u))
    return [u]
```