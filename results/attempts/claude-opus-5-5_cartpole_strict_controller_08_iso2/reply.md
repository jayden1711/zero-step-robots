This looks like a cart-pole: obs = [cart position, pole angle, cart velocity, pole angular velocity], with the action pushing the cart. I can't run it, so the controller below rests on an estimated model, not a test.

**Assumptions:**
- The action is a force of 100 N per unit of action.
- The cart is about 10.5 kg, and the pole is about 5 kg and 0.6 m long.
- A positive angle means the pole leans toward +x, so pushing toward +x corrects it.

If the angle's sign convention is the reverse of this, the controller will fail immediately.

**Model:** Linearised, the system is approximately:
- θ̈ ≈ 32.3·θ − 21.3·a
- ẍ ≈ 8.51·a − 3.13·θ

**Controller:** I used linear state feedback, a = k₁x + k₂ẋ + k₃θ + k₄θ̇. I chose the gains to put all four closed-loop poles at s = −4. That is slow enough for the 0.04 s step and fast enough to keep the angle well under 0.2.

```python
import numpy as np

# Linear state feedback: a = K . [x, theta, xdot, thetadot]
# Gains from pole placement (all closed-loop poles at s = -4) on a linearised cart-pole model.
K = np.array([1.23, 6.52, 1.23, 1.24])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    a = float(np.dot(K, s))
    a = max(-3.0, min(3.0, a))
    return [a]
```