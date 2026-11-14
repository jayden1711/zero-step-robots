This is a hand-tuned linear state-feedback controller, written without running it, so the gains are my estimates from the cart-pole dynamics.

- A positive pole angle means the pole leans toward +x, so pushing the cart toward +x when the pole leans that way keeps it upright.
- The cart position and velocity terms use the same sign as the angle terms, which is the usual cart-pole stabilising structure. They are kept small so they gently pull the cart back toward the centre without destabilising the pole.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 4.0 * th + 0.25 * v + 0.5 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
```