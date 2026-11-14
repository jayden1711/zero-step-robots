This is an untested design: a linear state-feedback controller realised through the tanh layer, with gains chosen by hand from a rough model of the physics.

- **Control law:** action = 0.1·x + 3.5·θ + 0.3·ẋ + 0.5·θ̇. Pushing the cart toward the lean (positive θ gives positive force) catches the pole.
- **Cart terms:** the small positive gains on x and ẋ are the non-minimum-phase LQR signs. They keep the cart from drifting off the rail.
- **tanh layer:** all 16 hidden units are identical and scaled to stay in the near-linear region of tanh. Each row is 0.5 times the gain vector, and each output weight is 0.125, so the 16 units sum to the intended linear gain.

```json
{
  "W1": [
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25],
    [0.05, 1.75, 0.15, 0.25]
  ],
  "b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  "W2": [[0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125]],
  "b2": [0]
}
```