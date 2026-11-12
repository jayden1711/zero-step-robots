The controller is a linear state-feedback law (pole placement) embedded in a single hidden unit. Its input scale is kept small (0.05) so that tanh stays in its near-linear region, and the output weight (20) undoes that scaling. I could not run anything, so the score is untested.

**Model.** I estimated the dynamics from the `InvertedPendulum` MJCF:
- Cart: capsule, about 10.5 kg.
- Pole: capsule 0.6 m long, about 5 kg, centre of mass at 0.3 m, inertia about the pivot about 0.6–0.64.
- Motor gear: 100.

Linearised, this gives:
- ẍ ≈ 8.5u − 3.1θ
- θ̈ ≈ 32.3θ − 21.3u

**Gains.** I placed all four closed-loop poles at −3.5 rad/s, which is slow enough to tolerate the 0.04 s zero-order hold. The resulting law is:

u ≈ 0.72·x + 5.25·θ + 0.82·ẋ + 0.99·θ̇

A positive angle means the pole leans toward +x, so the cart is pushed toward +x to catch it.

**Robustness check.** I also checked these gains against a lighter-cart model (a 4.2 kg cart) using the Routh criterion. The closed loop is still stable, so moderate errors in my mass estimates should not break it.

```json
{"W1": [[0.03605, 0.2625, 0.0412, 0.0493], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```