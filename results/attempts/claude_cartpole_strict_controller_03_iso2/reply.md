This is a guess at a standard cart-pole stabilizer, and I haven't run or tested it. I assumed the observations are `[cart position, pole angle, cart velocity, pole angular velocity]`, as in MuJoCo's InvertedPendulum. The controller is linear state feedback. All gains are positive because a positive pole angle needs a push toward positive cart position. The cart position and velocity terms are small and keep the cart from drifting. The gain values are my estimates from rough dynamics, not tuned.

```python
import numpy as np

def reset():
    pass

def act(obs):
    x, th, xd, thd = [float(v) for v in obs]
    u = 0.1 * x + 4.0 * th + 0.4 * xd + 0.6 * thd
    return [float(np.clip(u, -3.0, 3.0))]
```