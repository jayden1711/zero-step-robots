The controller is a linear state-feedback law, designed by pole placement on a linearized cart-pole model. It runs through one hidden unit kept in the near-linear range of tanh. I can't run it, so the result is unverified.

**Model.** I estimated the parameters from the MuJoCo XML:
- Cart about 10.5 kg, pole about 5 kg, pole centre of mass 0.3 m above the hinge.
- Actuator gear 100, so a force of u in the action means 100·u newtons.
- A positive pole angle tilts the pole toward +x.

Linearized, this gives:
- θ̈ ≈ 32.3θ − 21.3u
- ẍ ≈ 8.51u − 3.13θ

**Gains.** I placed the closed-loop poles at {−2, −2, −5, −5}, which gives:

u = 0.48·x + 4.95·θ + 0.672·ẋ + 0.926·θ̇

All gains are positive, which is what a cart-pole needs: the cart is pushed toward the side the pole leans to. The positive position gain is the usual non-minimum-phase term that brings the cart back to the centre. The poles are slow compared with the 0.04 s step, so the discrete-time loop should behave like the continuous design. They are also fairly robust if my mass estimates are somewhat off. The starting perturbations are tiny, so the action stays well inside the [−3, 3] clip.

**Network.** Hidden unit 0 computes tanh(0.05·(K·obs)), and the output multiplies it by 20. Over the range of states the controller should see, 0.05·(K·obs) stays small, so tanh is close to linear and the output reproduces K·obs. The other 15 units are set to zero.

```json
{
  "W1": [
    [0.024, 0.2475, 0.0336, 0.0463],
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