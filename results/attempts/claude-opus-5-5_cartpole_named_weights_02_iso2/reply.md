This controller is a linear state-feedback (LQR-style) law built into one tanh unit. It hasn't been run or tested, and the gains come from a rough hand estimate of the MuJoCo model, so the score is not known.

**How the gains were chosen**

- **Sign convention:** a positive pole angle means the pole leans toward +x, so the cart has to push toward +x to catch it.
- **Model estimate:** the cart and pole are each about 5 kg, the pole is 0.6 m long, and the actuator gear is about 100. That gives roughly θ̈ ≈ 24.5·θ − 37·u, where u is the action.
- **Pole loop:** I aimed for a natural frequency of about 8 rad/s with damping ratio about 0.7. That gives an angle gain of about 2.4 and an angular-velocity gain of about 0.3.
- **Cart loop:** the cart is held near the centre of the rail by a slower outer loop. Its position gain is 0.1 and its velocity gain is 0.2, both positive (a positive cart gain is what keeps this setup stable). This gives a time scale of about 1–2 s with damping ratio about 0.75.
- **Fitting it into the network:** one hidden unit computes tanh(0.2 · (k · obs)). The output weight is 5, which undoes the 0.2 scaling. Because the input to tanh stays small, the unit behaves almost linearly. All other units are zeroed.
- **Robustness:** with this much damping, the loop should stay stable even if my model estimate is off by a factor of about 2.

```json
{"W1": [[0.02, 0.48, 0.04, 0.06], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```