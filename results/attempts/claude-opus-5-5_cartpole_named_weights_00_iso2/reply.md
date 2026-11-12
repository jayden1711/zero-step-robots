I treated the network as a linear state-feedback controller, `force = K · obs`, and kept the tanh units in their near-linear range. I have not run this controller.

**Model.** I linearised the MuJoCo model about upright using values taken from its XML:
- The cart is about 10.5 kg and the pole about 5.0 kg, with its centre of mass 0.3 m above the hinge and inertia about the pivot of roughly 0.6 kg·m².
- The motor gear is 100, so an action `u` gives about 100·u newtons.
- A positive pole angle means the pole leans toward +x, because the hinge axis is +y.

This gives:
- θ̈ ≈ 32.3·θ − 21.3·u
- ẍ ≈ 8.51·u − 3.13·θ

**Gains.** With `u = a·x + b·θ + c·ẋ + d·θ̇`, the closed-loop characteristic polynomial is:

s⁴ + (21.3d − 8.51c)s³ + (21.3b − 8.51a − 32.3)s² + 208.2c·s + 208.2a

I placed the poles at {−3, −3, −6, −6}. These are slow enough to be robust at the 0.04 s step and fast enough to keep the cart well inside the ±1 m rail. That gives:

**a = 1.556, b = 7.63, c = 1.556, d = 1.467**

The position gain is positive, which looks backwards but is correct for cart-pole. It is needed for stability because the system is non-minimum phase.

**Embedding.**
- One hidden unit computes `tanh(0.05 · K·obs)`, and its output weight is 20. This stays nearly linear across the useful action range, and all other units are zero.
- For the expected tiny perturbations, the action stays far below the ±3 clip.

```json
{
  "W1": [
    [0.0778, 0.3815, 0.0778, 0.0734],
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