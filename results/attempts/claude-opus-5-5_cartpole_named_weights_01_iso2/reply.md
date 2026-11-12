The controller is a linear state-feedback law placed inside one hidden tanh unit. That unit is scaled down so tanh stays in its near-linear range, and the output weight scales it back up. All other hidden units have zero weight and do nothing.

**Model:** I estimated the dynamics from the MuJoCo model. The pole is about 5 kg with its centre of mass about 0.3 m up. The cart is about 10.5 kg. The actuator gear is about 100. Linearising gives:
- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ 8.5·u − 3.13·θ

**Sign:** A positive angle means the pole leans toward +x, so all four gains are positive.

**Gains:** I placed the closed-loop poles at (s+1.5)²(s+6)². That gives:
- u = 0.39·x + 5.16·θ + 0.65·ẋ + 0.963·θ̇

The fast poles at 6 rad/s are comfortable for the 0.04 s step.

**Embedding:** h₀ = tanh(0.05·(K·obs)) and action = 20·h₀. The tanh stays nearly linear up to the ±3 clip range.

These gains rest on my estimated masses and gear, and I couldn't run the simulation, so the score is untested.

```json
{
  "W1": [
    [0.0195, 0.258, 0.0325, 0.04815],
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
  "W2": [[20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
  "b2": [0.0]
}
```