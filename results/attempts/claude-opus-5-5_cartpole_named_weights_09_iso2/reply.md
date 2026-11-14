The controller is a linear stabilizing feedback law built into one tanh unit. I couldn't run it, so the gains come from a rough physics estimate and are not tested.

**Sign convention.** A positive pole angle means the pole leans toward +x. A positive force pushes the cart toward +x, which catches the pole.

**Rough model.** I estimated the model parameters from the MuJoCo model; these are approximate.
- Pole: about 5 kg, length 0.6 m.
- Cart: about 10 kg.
- Actuator gear: 100.

With these values the dynamics are roughly θ'' ≈ 24.5·θ − 20·u, and the cart acceleration is about 8·u.

**Pole loop.** With u = 2.5·θ + 0.5·θ̇, the pole loop settles at about 5 rad/s and is well damped. That speed is comfortably within what the 0.04 s step can handle.

**Cart loop.** Small gains of the same sign, 0.1·x + 0.2·ẋ, give a slow loop at about 0.9 rad/s that recentres the cart. This is the usual non-minimum-phase pattern for a cart-pole controller.

**Network layout.**
- One hidden unit computes tanh(0.1·z), where z is the full linear law.
- Its output weight is 10.
- At the maximum force, the tanh argument is only about 0.3, so the unit stays almost linear.
- All other units and biases are zero.

```json
{
  "W1": [
    [0.01, 0.25, 0.02, 0.05],
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
  "W2": [[10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
  "b2": [0.0]
}
```