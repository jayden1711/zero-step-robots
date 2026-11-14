I built a linear stabilizing controller and placed it inside the network. It was not tested: these are hand-derived weights.

**Physics model.** I used rough rigid-body estimates: a cart of about 10 kg, a pole of about 5 kg and 0.6 m, and an actuator gear of 100. That gives approximately:
- cart: ẍ ≈ a
- pole: θ̈ ≈ 24.5·θ − 2.5·a
- a ≈ 100·u / 15.5

**Feedback law.** With a = kθ·θ + kω·ω + kx·x + kv·v, I placed the closed-loop poles in two pairs:
- a fast pole-balancing pair with ωn = 7 and damping 0.7
- a slow cart-centring pair with ωn = 1.5 and damping 0.8

That gives kx = 4.5, kv = 5.7, kθ = 41.5 and kω = 7.2. Converted to action units, the law is:

u ≈ 0.70·x + 6.43·θ + 0.88·v + 1.11·ω

All four gains are positive. The pole rotates about the y-axis, so a positive angle means the pole is tilted toward +x, and the cart has to push toward +x to catch it.

**Embedding.** A single tanh unit computes tanh(0.1·(gains·obs)), and its output weight is 10. Near the equilibrium this is effectively linear. The tanh saturates at ±10, well past the ±3 action clip, so it never limits the controller. The other 15 units are zeroed.

```json
{"W1": [[0.070, 0.643, 0.088, 0.111], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "W2": [[10.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "b2": [0.0]}
```