This looks like MuJoCo's InvertedPendulum, with obs as [cart position, pole angle, cart velocity, pole angular velocity]. I couldn't run anything, so the controller is a linear state feedback with gains estimated from rough physics, and none of it has been tested.

The gains are all positive: pushing the cart toward the side the pole leans is what keeps it up. The pole-angle and angular-velocity gains do the balancing, and the small cart position and velocity gains stop the cart drifting off.

```python
import numpy as np

K = np.array([0.1, 5.0, 0.3, 0.6])


def reset():
    pass


def act(obs):
    u = float(np.dot(K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
```