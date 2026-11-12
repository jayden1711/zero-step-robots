This assumes the system is a cart-pole (MuJoCo InvertedPendulum style). I read `obs` as `[cart position, pole angle, cart velocity, pole angular velocity]`. The controller is a linear state-feedback law that pushes the cart toward the direction the pole leans. The small positive gains on cart position and velocity follow the LQR sign pattern and keep the cart from drifting. I couldn't run it, and the gains are estimates from rough dynamics, not tuned.

```python
import numpy as np

K = np.array([0.1, 5.0, 0.2, 1.0])


def reset():
    pass


def act(obs):
    u = float(np.dot(K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
```