This looks like a cart-pole: `obs = [cart position, pole angle, cart velocity, pole angular velocity]`. The rules match the classic MuJoCo InvertedPendulum: the action is a motor command (gear about 100), and the episode ends when the pole angle exceeds 0.2 rad.

I estimated the physical parameters from the standard model:

- Cart mass is about 10.5 kg.
- The pole is about 5 kg, 0.6 m long, with its centre of mass at 0.3 m.

Linearising gives:

- ẍ ≈ 8.51·u − 3.13·θ
- θ̈ ≈ 32.3·θ − 21.3·u

A linear state-feedback law `u = a·x + b·v + c·θ + d·ω` produces this characteristic polynomial:

s⁴ + (21.3d − 8.51b)s³ + (21.3c − 32.3 − 8.51a)s² + 208.2b·s + 208.2a

I placed all four poles at s = −4, i.e. (s+4)⁴ = s⁴ + 16s³ + 96s² + 256s + 256. This gives a ≈ 1.23, b ≈ 1.23, c ≈ 6.52 and d ≈ 1.24.

All gains are positive. The pole falling toward +x is corrected by pushing the cart toward +x. The cart-position terms slowly bring the cart back to the centre so it stays within its ±1 m rail.

```python
import numpy as np

# Linear state feedback (pole placement, all closed-loop poles near s = -4)
# obs = [cart_pos, pole_angle, cart_vel, pole_ang_vel]
K = np.array([1.23, 6.52, 1.23, 1.24])


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