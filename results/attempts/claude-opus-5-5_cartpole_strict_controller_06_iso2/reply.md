This looks like a cart-pole balance task, most likely MuJoCo `InvertedPendulum`. If so, the observation is `[cart position x, pole angle θ, cart velocity ẋ, pole angular velocity θ̇]`. The 0.04 s step, the ±3 action range, the |θ| ≤ 0.2 termination and the 1000-step limit all match that environment. I couldn't run anything, so the controller is untested.

**How I chose the gains.** I estimated the masses from that model's geometry: cart about 10.5 kg, pole about 4.9 kg with its centre of mass at 0.3 m, and an actuator gear of 100. That gives roughly θ̈ ≈ 32·θ − 21·a. Pushing the cart toward +x (positive action) rotates the pole toward negative θ, so the angle gain must be positive.

- **Inner loop (angle):** a PD controller with kθ ≈ 4.5 and kd ≈ 0.75. This targets about 8 rad/s, well damped, and is safe at a 0.04 s step.
- **Outer loop (cart position):** a slow loop that tilts the pole target to bring the cart back to the centre. This adds small positive gains on x and ẋ.
- **Output:** the action is clipped to ±3.

**Main risk.** The whole controller depends on the observation order and sign convention being as I assumed. If either differs, the controller will fail immediately.

```python
import numpy as np

# Inner (angle) loop gains
K_TH = 4.5
K_THD = 0.75
# Outer (cart position) loop: theta_ref = -(KP*x + KV*xdot)
KP = 0.05
KV = 0.15


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs[:4])
    if not np.all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    th_ref = -(KP * x + KV * xd)
    th_ref = max(-0.05, min(0.05, th_ref))
    a = K_TH * (th - th_ref) + K_THD * thd
    a = max(-3.0, min(3.0, a))
    return [a]
```