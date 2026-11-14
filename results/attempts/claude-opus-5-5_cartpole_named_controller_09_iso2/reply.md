This is a linear state-feedback controller, roughly LQR-style, tuned by hand from an approximate linearised model of the MuJoCo cart-pole. I couldn't run or test it, so the gains rest on that model alone.

**Model behind the gains**
- The actuator gear is 100, so an action of `u` gives about `100·u` newtons.
- The cart weighs about 10 kg and the pole about 5 kg, with the pole's centre of mass 0.3 m up.
- Linearised, that gives cart acceleration of about `6.5·u` and pole angular acceleration of about `24.5·θ − 16·u`.

**Sign convention**
- A positive angle means the pole's top leans toward +x.
- So the cart must push toward +x to catch it, and every gain is positive.
- The position gain is also positive because of the non-minimum-phase behaviour: to bring the cart back to 0, it first has to move outward so the pole tilts back toward the centre.

**Gains and stability**
- The gains are `kx=0.3, kv=0.6, kθ=6, kω=1.2`.
- The closed-loop characteristic polynomial under this model is `s⁴ + 15.3s³ + 69.5s² + 95.6s + 47.8`. It passes the Routh–Hurwitz test, so the loop is stable.
- Its fastest pole is around −12 rad/s, slow enough for the 0.04 s control step.
- The position loop is deliberately gentle. It keeps the cart from drifting into the rail limits over the 40-second episode without disturbing the pole balance.

```python
import numpy as np

# State feedback gains: [cart pos, pole angle, cart vel, pole ang vel]
K = np.array([0.3, 6.0, 0.6, 1.2])


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