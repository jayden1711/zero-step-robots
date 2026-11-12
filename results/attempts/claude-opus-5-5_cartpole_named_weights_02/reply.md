I treated the network as a linear state-feedback controller and picked the gains by pole placement on a linearized model.

**Model.** From the standard MuJoCo `inverted_pendulum.xml`:
- Cart is about 10.5 kg and the pole about 5 kg (0.6 m long).
- The motor gear is 100, so the force is 100 × action.
- A positive hinge angle means the pole tips toward +x.

Linearized, that gives approximately:
- x″ ≈ 8.4u − 3θ
- θ″ ≈ 31θ − 20.4u

**Gains.** Using u = a·x + b·v + c·θ + d·ω, the closed-loop characteristic polynomial is:

σ⁴ + (20.4d − 8.4b)σ³ + (20.4c − 8.4a − 31)σ² + 199.8b·σ + 199.8a

I placed the poles at (σ+2)²(σ+6)². That speed is slow enough to tolerate the 0.04 s zero-order hold and modelling errors, and fast enough to catch the pole. The result is:

| Gain | Value |
|---|---|
| a (cart position) | 0.72 |
| b (cart velocity) | 0.96 |
| c (pole angle) | 6.13 |
| d (pole angular velocity) | 1.18 |

**Embedding in the network.** Four hidden units compute tanh(0.5·obs_i). That stays nearly linear over the operating range. Each output weight is the gain divided by 0.5. The other 12 units are zeroed. I could not run this, so the score is untested.

```json
{"W1": [[0.5, 0.0, 0.0, 0.0], [0.0, 0.5, 0.0, 0.0], [0.0, 0.0, 0.5, 0.0], [0.0, 0.0, 0.0, 0.5], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[1.44, 12.26, 1.92, 2.36, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```