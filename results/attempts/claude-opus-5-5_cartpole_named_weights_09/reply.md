These weights are a hand-derived linear stabiliser. I had to estimate the cart and pole masses, so the gains depend on that rough model.

**Model.** In this environment a positive pole angle tilts the pole toward +x, and a positive action pushes the cart toward +x (the motor gear is about 100). I estimated a pole of about 5 kg and a cart of about 10 kg. That gives roughly θ̈ ≈ 37·θ − 25·a for the pole and ẍ ≈ 10·a − 3·θ for the cart.

**Control law.** a = 0.1·x + 4·θ + 0.2·ẋ + 0.5·θ̇

- **Pole loop:** the angle and angular-velocity gains give a closed-loop frequency of about 8 rad/s with good damping, which is well inside the stable range at a 0.04 s step.
- **Cart loop:** the small position and velocity gains have the same sign as the angle gains, which is the usual sign for this kind of system. They slowly pull the cart back toward the centre of the rail without upsetting the balance.

**Network.** Only one hidden unit is used. Its inputs are scaled down by 10 so tanh stays in its near-linear range (the input stays below about 0.2), and the output weight of 10 restores the gain. The other 15 units have zero weights and contribute nothing.

```json
{"W1": [[0.01, 0.4, 0.02, 0.05], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```