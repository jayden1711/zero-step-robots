This controller is a linear state-feedback controller built into the network. It uses one hidden unit with small input weights, so tanh stays in its near-linear range. The output weight undoes the scaling.

**Control law:** u ≈ 0.2·x + 4.0·θ + 0.3·ẋ + 0.5·θ̇

**Signs:**
- The hinge axis is +y, so a positive angle tilts the pole tip toward +x. Pushing the cart toward +x catches it, which is why the θ and θ̇ gains are positive.
- The x and ẋ gains are also positive. To move the cart back toward the centre, the cart must first lean the pole the other way. Analysing the slow position loop with these signs gives x'' ≈ −c·(k_x·x + k_v·ẋ), which is stable.

**Gain sizes:** I estimated the motor gear at 100, the cart at about 10 kg and the pole at about 5 kg over 0.6 m. That gives roughly θ'' ≈ 24.5·θ − (11 to 21)·u. With k_θ = 4 and k_ω = 0.5, the pole loop is stable and well damped across that whole range of uncertainty. The fastest mode is about 8 rad/s, which suits the 0.04 s step. The position loop is much slower, at about 1 rad/s.

**Network weights:**
- Hidden unit 0 has input weights equal to 0.05 × the gains. Its pre-activation stays below about 0.1, so tanh is almost exactly linear there.
- The output weight is 20, which undoes the 0.05 scaling.
- All other units, and all biases, are zero.

```json
{
  "W1": [[0.01, 0.2, 0.015, 0.025], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
  "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "W2": [[20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
  "b2": [0]
}
```