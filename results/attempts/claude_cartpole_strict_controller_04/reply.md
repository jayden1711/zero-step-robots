This looks like MuJoCo's InvertedPendulum: obs is [cart position, pole angle, cart velocity, pole angular velocity], and the episode ends when the pole angle passes 0.2 rad. I couldn't run or test anything, so the gains are an educated guess rather than tuned values.

The controller is a linear state-feedback law. The pole-angle and angular-velocity terms push the cart toward the side the pole is leaning. The small cart position and velocity terms are positive, which is the usual LQR sign for cart-pole. This keeps the cart from drifting off the track.

```python
import numpy as np

_K = np.array([0.3, 4.0, 0.5, 0.7])


def reset():
    pass


def act(obs):
    a = float(np.dot(_K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, a))]
```