This is my best guess at the environment, since I can't run anything. I think it is MuJoCo's InvertedPendulum, with obs = [cart x, pole angle, cart velocity, pole angular velocity]. The controller is a linear state-feedback law with a positive gain on every term. Pushing the cart toward the lean corrects the angle. The small positive gains on cart position and velocity pull the cart back toward the center. The gains are estimated from rough dynamics, not tuned.

```python
import numpy as np

K = np.array([0.2, 5.0, 0.4, 0.6])


def reset():
    pass


def act(obs):
    u = float(np.dot(K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
```