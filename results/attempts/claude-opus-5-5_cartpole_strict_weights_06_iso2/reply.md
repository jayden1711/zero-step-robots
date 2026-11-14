This appears to be the MuJoCo InvertedPendulum task. The observation is [cart position, pole angle, cart velocity, pole angular velocity], and the action is the cart force with gear 100.

**Model.** I estimated the masses from the model geometry and linearised the dynamics:
- cart acceleration ≈ 8.5u − 3.1θ
- pole angular acceleration ≈ 32θ − 21u

**Controller.** From that model I used pole placement:
- The fast pole loop targets a natural frequency of about 8 rad/s with damping ratio about 0.7.
- The slow cart loop targets about 1 rad/s.

That gives the linear law:

u = 0.2·x + 4.5·θ + 0.35·ẋ + 0.53·θ̇

**Network.** One tanh unit carries this law. Its input weights are 0.05× the gains and its output weight is 20, so tanh stays almost linear over the operating range. The other 15 units are zeroed out.

```json
{
  "W1": [
    [0.01, 0.225, 0.0175, 0.0265],
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
  "W2": [[20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
  "b2": [0.0]
}
```