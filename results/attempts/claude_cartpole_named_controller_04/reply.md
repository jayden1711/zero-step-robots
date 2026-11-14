I couldn't run or test this, so the gains are chosen from the physics rather than tuned. The controller is a stateless linear state-feedback law on all four observations, a form that normally balances this pendulum for the full 1000 steps.

In this environment a positive pole angle means the pole leans toward +x, so pushing the cart toward the lean (positive gain on angle and angular velocity) catches it. The cart position and velocity terms carry the same sign, which is the usual LQR structure for a cart-pole. They are kept small so they gently pull the cart back toward the centre without destabilising the pole.

```python
def act(obs):
    x, theta, xdot, thetadot = obs
    u = 0.2 * x + 0.5 * xdot + 12.0 * theta + 1.5 * thetadot
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
```