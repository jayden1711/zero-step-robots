I couldn't run or test this, so the gains below are estimated by hand from the model's approximate masses and geometry, not tuned.

The controller is linear state feedback. A positive pole angle means the pole leans toward +x, so pushing the cart toward +x catches it. For the same reason, the cart-position and cart-velocity terms also carry a positive sign. That sign looks odd but is correct: to bring the cart back, the pole first has to be tilted toward the centre.

```python
import numpy as np

K = np.array([0.1, 5.0, 0.5, 0.6])


def reset():
    pass


def act(obs):
    u = float(np.dot(K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
```