This is a linear state-feedback controller. I couldn't run it, so the gains come from a rough hand model of the cart-pole, not from simulation.

The sign convention is that a positive pole angle means the pole leans toward +x, so the cart is pushed in the direction of the lean. The cart position and velocity terms have the same sign, which is the usual cart-pole LQR structure and pulls the cart back toward the centre over time. The pole terms dominate (angle gain 3.0, angular-velocity gain 0.4) and the cart terms are small, so the pole loop is fast and the cart loop is slow. The output is clipped to [-3, 3].

```python
def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 3.0 * th + 0.2 * xd + 0.4 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
```