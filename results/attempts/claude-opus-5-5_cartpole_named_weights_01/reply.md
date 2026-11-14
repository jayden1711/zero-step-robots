The controller is a linear state-feedback law placed inside the network. One hidden unit runs in tanh's linear region: its input weights are scaled by 0.01, and the output weight of 100 undoes that scaling. The other 15 units are zeroed.

**Model and gains**
- I estimated the physics from the MuJoCo model: cart about 10.5 kg, pole about 5 kg and 0.6 m long, motor gear 100.
- Linearising gives roughly
  - pole: θ̈ ≈ 32.3θ − 21.3u
  - cart: ẍ ≈ 8.51u − 3.13θ
- With u = a·x + b·v + c·θ + d·ω, the closed-loop characteristic polynomial is s⁴ + (21.3d − 8.51b)s³ + (21.3c − 8.51a − 32.3)s² + 208.2b·s + 208.2a.
- Placing all four poles at s = −4 gives a ≈ 1.23, b ≈ 1.23, c ≈ 6.51 and d ≈ 1.243.
- All the gains are positive. A pole tilting toward +x needs a +x push, and the positive cart-position gain is the usual non-minimum-phase recentering term.
- The forces stay well inside the ±3 limit for the tiny initial perturbations. The tanh input stays below about 0.05, so the unit behaves linearly.

```json
{
  "W1": [
    [0.0123, 0.0651, 0.0123, 0.01243],
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
  "W2": [[100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
  "b2": [0.0]
}
```