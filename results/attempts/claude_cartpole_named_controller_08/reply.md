I haven't run this, since I can't run anything here. It's a linear state-feedback controller, `u = 3.0·θ + 0.35·θ̇ + 0.1·x + 0.2·ẋ`, with the gains chosen by hand from approximate pole dynamics.

- **Pole terms:** a positive angle tips the pole toward +x, so the cart is pushed toward +x to get under it. The θ̇ term adds damping.
- **Cart terms:** these use the same sign as the pole terms, as in the usual LQR solution for a cart-pole. They are kept small so the cart is slowly pulled back toward the centre without destabilising the pole.

```python
import numpy as np

K = np.array([0.1, 3.0, 0.2, 0.35])


def reset():
    pass


def act(obs):
    u = float(np.dot(K, np.asarray(obs, dtype=float)))
    return [max(-3.0, min(3.0, u))]
```