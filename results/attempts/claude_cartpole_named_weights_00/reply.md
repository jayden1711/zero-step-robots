This is an untested controller. It is a linear state-feedback law, `action = 0.5·x + 20·θ + 1·ẋ + 3·θ̇`, built from four of the tanh units. Each unit sees one observation scaled by 0.1, so it stays in tanh's near-linear range, and the output weights multiply the gain back up. The other 12 units are zeroed out.

The gains come from rough dynamics estimates, not from a simulation:
- **Angle and angular velocity:** the large positive gains push the cart toward the lean, which is the sign that stabilises the pole.
- **Cart position and velocity:** these gains are small and also positive, since the cart-position term needs the same sign as the angle term. They keep the cart from drifting off the rail.

```json
{
  "W1": [
    [0.0, 0.1, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.1],
    [0.1, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.1, 0.0],
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
  "W2": [[20.0, 3.0, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
  "b2": [0.0]
}
```