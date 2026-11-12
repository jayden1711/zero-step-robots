This is almost certainly MuJoCo **InvertedPendulum**: obs = [cart position, pole angle, cart velocity, pole angular velocity], action = motor force (gear 100, range ±3), dt = 0.04, and the episode ends when the pole angle exceeds 0.2 rad.

**Approach.** I used a linear state-feedback controller, u = kx·x + kθ·θ + kv·v + kω·ω, and placed it inside a single tanh unit.

**Sign convention.** With the hinge about +y, a positive θ means the pole leans toward +x. The cart must then accelerate toward +x to get back under the pole.

**Gains.** A reduced model gives roughly θ'' ≈ 24.5θ − 16u and x'' ≈ 6.5u. With those, the closed-loop characteristic polynomial is:

s⁴ + (16kω − 6.5kv)s³ + (16kθ − 6.5kx − 24.5)s² + 159kv·s + 159kx

I placed the poles at (s+8)²(s+1.5)², which gives:

- kx ≈ 0.906
- kθ ≈ 9.04
- kv ≈ 1.43
- kω ≈ 1.77

All gains are positive, which is required for stability.

**Network encoding.**
- Hidden unit 0 takes 0.05 × the gains, so it stays in tanh's linear region.
- W2[0] = 20 undoes that scaling.
- All other units are zeroed.

```json
{
  "W1": [
    [0.0453, 0.452, 0.0717, 0.0885],
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