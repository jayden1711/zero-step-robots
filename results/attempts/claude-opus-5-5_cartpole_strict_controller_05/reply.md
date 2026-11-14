This looks like a cart-pole balancing task: obs is [cart position, pole angle, cart velocity, pole angular velocity], with termination at a pole angle of 0.2 rad. The controller below is a linear state-feedback (LQR-style) policy.

**How the gains were chosen**
- **Sign:** pushing the cart in +x drives the pole angle down. So to correct a positive angle, the action must be positive.
- **Pole dynamics:** I used a rough linear model, θ̈ ≈ 32θ − 21u. That makes 1.5 the smallest angle gain that can hold the pole up.
- **Balance loop:** gains of 4.5 on angle and 0.6 on angular velocity give a fast, well-damped response, about 8 rad/s with roughly 0.8 damping. That is about 3× the minimum, which leaves room if the masses differ from my model.
- **Cart loop:** small positive gains on position and velocity slowly bring the cart back to centre without overloading the balance loop. The positive sign is deliberate: the cart steps out first so the pole tips back toward centre.
- **Saturation:** at the 0.2 rad limit the angle term asks for about 0.9, well inside the ±3 action range.

I could not run this, so the gains have not been tested against the simulation.

```python
import numpy as np

# State feedback: [cart position, pole angle, cart velocity, pole angular velocity]
K = np.array([0.4, 4.5, 0.6, 0.6])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
```