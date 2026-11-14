I treated this as the MuJoCo InvertedPendulum cart-pole and designed a linear state-feedback controller. I could not run anything, so the gains rest only on a hand-derived physics model.

**System identification (inferred, not tested):** The observation is assumed to be `obs = [cart position x, pole angle θ, cart velocity v, angular velocity ω]`. Positive θ is taken to mean the pole leans toward +x. The action is assumed to be a cart force of 100·u N.

**Model:** I estimated the masses from the geometry: cart about 10.5 kg, pole about 5 kg, pole length 0.6 m. The linearised dynamics are then roughly:
- θ̈ ≈ 32.3θ − 21.3u
- ẍ ≈ 8.51u − 3.13θ

**Gains:** With feedback u = kx·x + kθ·θ + kv·v + kω·ω, the closed-loop characteristic polynomial is:

s⁴ + (21.3kω − 8.51kv)s³ + (21.3kθ − 32.3 − 8.51kx)s² + 208kv·s + 208kx

I placed all four poles at s = −4.5. That is a moderate speed for a 25 Hz control rate and an unstable open-loop pole near 5.7 rad/s. The resulting gains are:
- kx ≈ 1.97
- kθ ≈ 8.01
- kv ≈ 1.75
- kω ≈ 1.54

All four gains are positive. When the cart is displaced in +x, it first pushes further +x to tip the pole back toward the origin.

**Network encoding:** One tanh unit carries the gains scaled by 0.05, so it stays in its near-linear range, and its output weight is 20 to undo the scaling. Every other weight and bias is 0.

**Main risk:** If the angle sign convention is the opposite of what I assumed, this controller fails immediately. The model masses are also estimates.

```json
{"W1": [[0.0985, 0.4005, 0.0875, 0.077], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "W2": [[20.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], "b2": [0]}
```