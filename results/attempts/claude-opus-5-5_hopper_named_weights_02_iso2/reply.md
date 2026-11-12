This controller makes the hopper stand still rather than hop forward. I couldn't test anything, and a hand-written hopping gait is very likely to fall early. Standing upright safely should earn about 1 per step, so roughly **~1000 per episode**, if the hopper stays healthy for the full 1000 steps.

**How it works:** each joint gets a stiff spring-and-damper that pulls it back to 0 rad.

- **Hidden units 0, 1, 2:** each one computes `tanh(0.5·(q + 0.1·q̇))` for one joint (thigh, leg, foot). This stays nearly linear for small errors.
- **Output weights of −10:** these turn each unit into a torque of about `−5·q − 0.5·q̇`. That is 1000 N·m/rad of stiffness and 100 N·m·s/rad of damping after the 200× gear. Outputs are clipped at ±1, so large errors give full torque.
- **Why it should balance:** the joint armature and damping in Hopper's model should keep these gains stable at the 0.008 s control step. With the joints held straight, the robot becomes one rigid stick. Its centre of mass sits over the foot, which spans −0.13 to +0.26 m, so the small starting perturbations should die out instead of tipping it over.
- **Unused units:** the other 13 hidden units have zero weights.

```json
{
"W1": [
[0,0,0.5,0,0,0,0,0,0.05,0,0],
[0,0,0,0.5,0,0,0,0,0,0.05,0],
[0,0,0,0,0.5,0,0,0,0,0,0.05],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0]
],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[-10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-10,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-10,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```