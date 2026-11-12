The controller is a linear state-feedback (LQR-style) controller placed inside the network. The weights scale the input to unit 0 down by 0.1 so its tanh stays in its near-linear range, and `W2` multiplies it back up by 10. All other units are zero.

I worked out the gains from a linearised model of the MuJoCo cart-pole. I assumed a cart of about 10.5 kg, a pole of about 5 kg and 0.6 m, and an actuator gear of 100. These values came from my recollection of the model file and were not checked. The resulting policy is:

`action ≈ 0.12·x + 2.69·θ + 0.17·ẋ + 0.33·θ̇`

- **Angle and angular-velocity terms:** these hold the pole upright quickly, with a natural frequency of about 5 rad/s and good damping.
- **Small positive cart-position and cart-velocity terms:** these slowly bring the cart back toward the centre, at about 1 rad/s. The sign is positive because the cart must first tilt the pole toward the centre before it can move there.

```json
{
  "W1": [
    [0.012, 0.269, 0.017, 0.033],
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
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0]
  ],
  "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "W2": [[10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
  "b2": [0.0]
}
```