I wrote a linear state-feedback controller, assuming this is the MuJoCo inverted-pendulum cart-pole. I couldn't run or test it, and the gains are estimates from that assumption. The assumed obs layout is `[cart pos, pole angle, cart vel, pole angular vel]`, with a positive action pushing the cart toward the side the pole leans.

The pole angle and angular-velocity terms push the cart under the pole to catch it. The small cart position and velocity terms, with the same sign as the pole terms, pull the cart back toward the center, which is what a cart-pole LQR does.

```python
def reset():
    pass


def act(obs):
    x, th, v, w = obs[0], obs[1], obs[2], obs[3]
    u = 0.1 * x + 3.0 * th + 0.3 * v + 0.5 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
```