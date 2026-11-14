This uses a single tanh unit as an essentially linear state-feedback controller. The other 15 units are zeroed out.

**Sign convention.** The hinge axis is +y, so a positive angle means the pole leans toward +x. A positive action pushes the cart toward +x.

**Model estimates.** I worked these out from the MuJoCo model:
- Pole is about 5 kg with its centre of mass about 0.3 m up.
- Cart is about 10.5 kg.
- Actuator gear is 100.

Linearised, this gives roughly θ̈ ≈ 24.5·θ − 16·u.

**Control law.** I chose u = 0.1·x + 3.1·θ + 0.2·ẋ + 0.5·θ̇.
- **Inner pole loop:** natural frequency about 5 rad/s and well damped, which is safe for the 0.04 s step.
- **Outer cart loop:** slow and well damped, with positive gains on position and velocity. This is the usual non-minimum-phase cart-pole structure.

**Network encoding.** The unit computes h = tanh(0.05·(gains·obs)), and the output weight is 20. In the operating range the tanh stays close to linear.

```json
{
  "W1": [
    [0.005, 0.155, 0.01, 0.025],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ],
  "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "W2": [[20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
  "b2": [0]
}
```