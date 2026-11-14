This looks like a cart-pole balance task: obs = [cart position, pole angle, cart velocity, pole angular velocity], with termination when |angle| > 0.2. The controller is a linear state-feedback law built as a cascade:

- **Inner loop:** a PD controller on the pole angle. It pushes the cart toward the side the pole leans.
- **Outer loop:** a slow position loop. It shifts the target angle slightly so the cart drifts back toward the centre.

All gains are positive. A positive angle tilts the pole top toward +x, so the cart has to push +x to catch it. To bring a cart at x > 0 back, the pole first has to lean toward −x.

A rough linear model, assuming MuJoCo-style masses and an actuator gear of about 100, gives θ̈ ≈ 19.7θ − 13a. With these gains:

- The angle loop is roughly critically damped, at about 6–7 rad/s.
- The position loop is about 5× slower, so the two loops don't fight each other.
- The gains stay small compared with the ±3 action limit for the tiny initial perturbations.

I couldn't test this, so the signs and gains rest on that model, not on any simulation output.

```python
import numpy as np

# State-feedback gains: action = K . [x, theta, x_dot, theta_dot]
# Inner loop (pole angle PD) with a slow outer loop on cart position/velocity
# folded in via a shifted angle reference: theta_ref = -(KP_X*x + KD_X*x_dot).
K_THETA = 5.0
K_OMEGA = 1.0
KP_X = 0.06
KD_X = 0.12


def reset():
    pass


def act(obs):
    x = float(obs[0])
    theta = float(obs[1])
    x_dot = float(obs[2])
    theta_dot = float(obs[3])

    if not all(np.isfinite([x, theta, x_dot, theta_dot])):
        return [0.0]

    theta_ref = -(KP_X * x + KD_X * x_dot)
    theta_ref = float(np.clip(theta_ref, -0.08, 0.08))

    a = K_THETA * (theta - theta_ref) + K_OMEGA * theta_dot
    a = float(np.clip(a, -3.0, 3.0))
    return [a]
```