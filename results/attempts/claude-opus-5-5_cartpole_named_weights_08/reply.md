I built a PD-style (LQR-like) linear controller and embedded it in one tanh unit. The other 15 units are zeroed. None of this has been run: the gains come from a hand-derived linear model of the MuJoCo cart-pole, so the score is a prediction.

**Model behind the gains**
- Assumed physical values: actuator gear about 100, cart about 10.5 kg, pole about 5 kg with its centre of mass about 0.3 m above the hinge.
- From those, the linearised dynamics are roughly θ̈ ≈ 24.5·θ − 16·a and ẍ ≈ 6.5·a.

**Control law**
- I chose action ≈ 0.2·x + 6·θ + 0.3·ẋ + 1.0·θ̇.
- For the pole, this gives a natural frequency of about 8.5 rad/s with near-critical damping, which is reasonable at a 0.04 s step.
- For the cart, the slow loop that brings it back to centre is also stable.
- All gains are positive. A positive angle (pole leaning toward +x) is caught by pushing the cart toward +x.

**How it sits in the network**
- Unit 0 computes tanh(K·obs / 6), and the output weight is 6. Near zero this is linear, and it saturates smoothly as the action approaches the ±3 limit.

```json
{"W1": [[0.0333, 1.0, 0.05, 0.1667], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```