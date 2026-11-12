This is a linear state-feedback controller. I could not run it, so the gains are hand-estimated rather than tuned. A positive pole angle means the pole leans toward +x, so the controller pushes the cart toward the lean. The cart position and velocity terms have the same sign and are small, which keeps the cart near the centre of the rail without destabilising the pole.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 3.0 * th + 0.2 * xd + 0.5 * thd
    return [max(-3.0, min(3.0, u))]
```