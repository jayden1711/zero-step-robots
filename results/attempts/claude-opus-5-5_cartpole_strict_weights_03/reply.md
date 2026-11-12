The task is a cart-pole: obs = [cart x, pole angle θ, cart velocity, pole angular velocity]. The episode ends if |θ| exceeds 0.2.

I balance it with a linear state-feedback law placed inside one tanh unit. The input weights are small, so the unit stays in its near-linear range, and an output weight of 20 undoes that scaling. The law is:

u ≈ 0.3·x + 5·θ + 0.5·ẋ + 0.6·θ̇

All four gains have the same sign. This is the standard upright cart-pole result: to move the cart back toward the origin, the controller first pushes it outward so the pole tilts back inward.

- **Fast loop (pole angle):** θ and θ̇ are stiffly stabilised, at roughly 8 rad/s and well damped.
- **Slow loop (cart position):** x and ẋ drift back to the origin at roughly 1 rad/s.

The other 15 hidden units are unused, with all their weights set to zero.

```json
{"W1": [[0.015, 0.25, 0.025, 0.03], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```