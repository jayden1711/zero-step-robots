This controller is a linear state-feedback (PD) law built into the network. Only one hidden unit is used, with small input weights so that tanh stays close to linear. The other 15 units are zeroed.

**Control law** (approximately, while the action is not clipped):

`action ≈ 0.10·x + 3.0·θ + 0.15·ẋ + 0.40·θ̇`

**Signs.** The hinge rotates about +y, so a positive angle tips the pole toward +x. A positive force pushes the cart toward +x. To catch the pole, the cart therefore pushes in the direction the pole leans, which is why the angle gains are positive. To bring the cart back to the centre of the rail, the controller has to tilt the pole toward the centre first. That is why the position and velocity gains are also positive and kept small.

**Gain sizing.** The actuator gear is about 100. The cart is about 10.5 kg and the pole about 5 kg, with its centre of mass at 0.3 m. A rough linearized model gives θ̈ ≈ 29θ − 19u.

- **Angle loop:** With these gains the angle loop has a natural frequency of about 5–8 rad/s and a damping ratio of about 0.7–0.9. That holds across two different modelling approximations.
- **Discrete step:** At dt = 0.04 s this is still well inside the stable range for discrete-time control.
- **Position loop:** The cart-position loop is slow, around 1 rad/s, and well damped. The cart should stay away from the rail limits without disturbing the balance.

**Linearity of tanh.** The tanh input is 0.1 × action. For actions up to about 3, that keeps tanh nearly linear (tanh(0.3) ≈ 0.29). W2 = 10 undoes the 0.1 scaling.

```json
{"W1": [[0.01, 0.3, 0.015, 0.04], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```