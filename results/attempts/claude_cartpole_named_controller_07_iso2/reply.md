This is a linear state-feedback controller. I could not run or test it, and its gains are estimated from rough physics (about 100 N per unit action, a light cart and pole), not tuned.

A positive pole angle means the pole leans toward +x, so pushing the cart toward +x corrects it. The cart position and velocity terms also have positive sign. This is the non-minimum-phase behaviour: to bring the cart back, you first have to tilt the pole the right way. The cart gains are kept small so the pole loop dominates.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 4.0 * th + 0.6 * w + 0.1 * x + 0.2 * v
    return [max(-3.0, min(3.0, u))]
```