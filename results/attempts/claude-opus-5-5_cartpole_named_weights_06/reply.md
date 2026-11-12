The design is a linear state-feedback (pole-placement) controller, embedded in a single tanh unit kept in its near-linear range.

**Approximate model.** I estimated the parameters from the standard `InvertedPendulum` MJCF: actuator gear about 100, cart about 10.5 kg, pole about 5 kg with its centre of mass at 0.3 m. Linearising gives:

- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ 8.51·u − 3.13·θ

**Gains.** With u = k₁x + k₂ẋ + k₃θ + k₄θ̇, the closed-loop characteristic polynomial is:

s⁴ + (21.3k₄ − 8.51k₂)s³ + (21.3k₃ − 8.51k₁ − 32.3)s² + 208.2k₂s + 208.2k₁

Placing all four poles at s = −4, which is well within what a 0.04 s step can handle, gives:

- k₁ ≈ 1.23 (cart position)
- k₂ ≈ 1.23 (cart velocity)
- k₃ ≈ 6.52 (pole angle)
- k₄ ≈ 1.24 (pole angular velocity)

All four gains are positive. A positive pole angle means the pole leans toward +x, so the cart is pushed toward +x to catch it. The positive gain on cart position reflects the cart-pole's non-minimum-phase behaviour: to return to the origin, the cart must first let the pole lean toward the origin.

**Network.** One hidden unit uses these gains scaled by 0.05, so the tanh input stays below about 0.13 even when the pole is at 0.2 rad, which keeps it essentially linear. The output weight of 20 undoes the scaling. All other units are zero. With observations ordered [x, θ, ẋ, θ̇], the controller computes:

action ≈ 1.23x + 6.52θ + 1.23ẋ + 1.24θ̇

I could not run this, so the gains rest on my estimates of the model's masses and actuator gear.

```json
{"W1": [[0.0615, 0.326, 0.0615, 0.062], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```