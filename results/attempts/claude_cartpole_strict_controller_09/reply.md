This assumes the observation is `[cart position, pole angle, cart velocity, pole angular velocity]` (the MuJoCo InvertedPendulum layout). The controller is a linear feedback law, and I couldn't run or tune it here, so the gains are my best estimate.

- **Pole terms:** push the cart toward the side the pole is leaning, plus damping on the angular velocity.
- **Cart terms:** small gains with the same sign as the pole terms. This is the non-minimum-phase correction: to bring the cart back, you first push it away so the pole tilts the right way.

```python
import numpy as np

_K = np.array([0.15, 6.0, 0.3, 0.8])


def reset():
    pass


def act(obs):
    u = float(np.dot(_K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
```