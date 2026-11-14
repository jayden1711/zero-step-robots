This looks like a cart-pole: obs[0] is cart position, obs[1] is pole angle, obs[2] is cart velocity and obs[3] is pole angular velocity. The action is the cart force. I used a linear state-feedback controller, with gains taken from a rough linearised model.

**Rough model** (estimated, not measured):
- Cart about 10.5 kg, pole about 5 kg with its centre of mass about 0.3 m up.
- About 100 N of force per unit of action.
- Linearised, this gives roughly θ̈ ≈ 32θ − 21a.

**Gains:**
- **Pole loop:** a = 4.5·θ + 0.56·θ̇. This puts the pole's natural frequency near 8 rad/s with damping ratio about 0.75. That is fast enough to catch the instability and still well-behaved at a 0.04 s step.
- **Cart loop:** a slower loop with natural frequency about 1 rad/s, so the cart drifts back to the centre of the track. Its gains have the same sign as the pole gains. To move the cart back, the controller first has to tip the pole toward the centre.

```python
import numpy as np

K_X = 0.2      # cart position
K_TH = 4.5     # pole angle
K_V = 0.4      # cart velocity
K_W = 0.56     # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    a = K_X * x + K_TH * th + K_V * v + K_W * w
    if not np.isfinite(a):
        a = 0.0
    return [float(np.clip(a, -3.0, 3.0))]
```