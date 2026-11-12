I'm reading this as the classic inverted pendulum on a cart. My working assumptions:

- `obs = [cart position, pole angle, cart velocity, pole angular velocity]`
- The episode ends when |angle| > 0.2.
- A positive action pushes the cart in the direction the pole leans when its angle is positive.

I used a linear state-feedback (LQR-style) controller and built it into the network. Four hidden units run in tanh's near-linear range, each with input scale 0.1. The output weights are set to gain / 0.1. The other 12 units are zero.

The control law is:

**u ≈ 0.3·x + 8·θ + 0.7·ẋ + 1.2·θ̇**

- The angle loop is fast, with ω ≈ 10 rad/s and good damping at dt = 0.04 s.
- The cart-position loop is slow. Its positive gains pull the cart back by first tilting the pole.

```json
{
  "W1": [
    [0.1, 0.0, 0.0, 0.0],
    [0.0, 0.1, 0.0, 0.0],
    [0.0, 0.0, 0.1, 0.0],
    [0.0, 0.0, 0.0, 0.1],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0]
  ],
  "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "W2": [
    [3.0, 80.0, 7.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ],
  "b2": [0.0]
}
```