I treated the network as a linear state-feedback controller. One tanh unit runs in its near-linear range and the other 15 units are zeroed out. I couldn't run anything, so this is untested, and the gains come from rough estimates rather than the exact model.

**How I got the gains**

1. **Sign convention.** The pole hinge rotates about the y-axis, so I took positive angle to mean the pole leans toward +x. A positive force pushes the cart toward +x. If this sign is wrong, the controller will fail immediately.
2. **Approximate model.** From the default MuJoCo geometry I estimated:
   - cart mass about 10.5 kg and pole mass about 5 kg
   - motor gear of 100, so the action is scaled to newtons
   - linearised dynamics:
     - pole: θ̈ ≈ 32.3·θ − 21.3·u
     - cart: ẍ ≈ 8.5·u − 3.1·θ
3. **Pole placement.** I put the closed-loop poles at s = −1.5, −1.5, −6 and −6.
   - That gives u ≈ 0.388·x + 0.647·ẋ + 5.16·θ + 0.962·θ̇.
   - All four gains are positive. The positive gain on cart position is expected: to move the cart left, it first pushes right so the pole tips left.
   - The fastest pole times the step length is 6 × 0.04 = 0.24, which should be small enough for the discrete steps to stay stable.
4. **Fitting it into the network.**
   - Hidden unit 0 gets 0.05 times the gains, so its input stays small and tanh is almost linear.
   - The output weight for that unit is 20, which undoes the 0.05 scaling.
   - The other units and all biases are zero.
   - The angle gain (5.16) is well above the minimum needed to beat gravity (about 1.5), so the controller should tolerate some error in my mass estimates.

```json
{"W1": [[0.0194, 0.258, 0.03235, 0.0481], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```