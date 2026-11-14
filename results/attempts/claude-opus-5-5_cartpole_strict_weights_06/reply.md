This environment matches MuJoCo's InvertedPendulum: obs = [cart x, pole angle θ, cart velocity, pole angular velocity], action × gear 100 = force, dt = 0.04 s, terminate at |θ| > 0.2.

**Model.** The cart is about 10.5 kg and the pole about 5 kg. The pole's centre of mass is about 0.3 m above the pivot. Linearising gives:

- ẍ ≈ 8.51·a − 3.13·θ
- θ̈ ≈ 32.3·θ − 21.3·a

**Controller.** I used a linear law a = k·obs. The characteristic polynomial is:

s⁴ + (21.3k₄ − 8.51k₃)s³ + (21.3k₂ − 8.51k₁ − 32.3)s² + 208.2k₃·s + 208.2k₁

Placing the closed-loop poles at {−2, −2, −6, −6} gives the target s⁴ + 16s³ + 88s² + 192s + 144. Solving for the gains:

k = [0.692, 5.92, 0.922, 1.12]

**Embedding in the network.** One tanh unit carries the whole law. Its input weights are the gains scaled by 0.05, and its output weight is 20. With those scales the unit stays in its near-linear range, so the network computes the linear law almost exactly. All other units are zero.

```json
{
  "W1": [
    [0.0346, 0.296, 0.0461, 0.056],
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