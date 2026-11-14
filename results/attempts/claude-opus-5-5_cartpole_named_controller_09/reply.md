This is a fixed-gain linear (LQR-style) state-feedback controller.

**Sign convention.** The hinge rotates about the y-axis. A positive pole angle means the pole leans toward +x. To catch it, the controller pushes the cart toward +x. With this convention, all four feedback gains are positive.

**Where the gains come from.** I estimated masses from the MuJoCo model geometry (default density):

- cart ≈ 10 kg
- pole ≈ 5 kg, length 0.6 m
- actuator gear ≈ 100, so u = 1 gives about 100 N

From those, the pole loop is designed for about 6 rad/s with damping near 0.8. That is fast enough to hold the pole well inside ±0.2 rad, but slow compared with the 0.04 s step.

**Cart position.** A slow outer loop on cart position and velocity keeps the cart from drifting off the rail over 1000 steps. It does this by asking for a slight lean of the pole back toward the centre.

**Caveat.** I couldn't run this, and the gains rest on mass estimates rather than measurements.

```python
import numpy as np

# State feedback gains: u = K . [x, theta, x_dot, theta_dot]
# Pole terms stabilise the pendulum; small cart terms keep the cart centred.
K_X = 0.08
K_TH = 3.8
K_V = 0.2
K_W = 0.6


def reset():
    pass


def act(obs):
    x, th, v, w = (float(o) for o in obs[:4])
    if not all(np.isfinite([x, th, v, w])):
        return [0.0]
    u = K_X * x + K_TH * th + K_V * v + K_W * w
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
```