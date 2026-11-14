This looks like the classic cart-pole balancing task. I assumed the observation is `[cart position, pole angle, cart velocity, pole angular velocity]`, with the pole angle at index 1 since that is the one that ends the episode. I also estimated the physical parameters from typical values: cart about 10.5 kg, pole about 5 kg and 0.6 m long, and an actuator gain of about 100 N per unit of action. Nothing here was run or tested.

With those estimates, the linearised dynamics are roughly:

- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ 8.51·u − 3.13·θ

With feedback u = a·x + b·θ + c·ẋ + d·θ̇, the closed-loop characteristic polynomial works out to:

p⁴ + (21.3d − 8.51c)p³ + (21.3b − 8.51a − 32.3)p² + 208.2c·p + 208.2a

I placed all four poles at −5. That gives a ≈ 3.0, b ≈ 9.76, c ≈ 2.40 and d ≈ 1.90. A pole at −5 moves only about 0.2 per 0.04 s step, so this sampling rate should be fine.

If my guesses about the parameters or sign conventions are wrong, the controller could perform badly.

```python
import numpy as np

# State feedback u = K . [x, theta, x_dot, theta_dot]
# Gains from pole placement (all closed-loop poles near -5) on the
# linearised cart-pole model.
K = np.array([3.0, 9.76, 2.40, 1.90])


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