I haven't run this, so it is an untested best guess. It is a hand-designed PD stabiliser aimed at keeping the hopper upright for the full 1000 steps, not at hopping fast.

- **Hidden unit 0 (thigh):** feeds back torso angle and angular velocity, so a backward lean produces a forward-correcting hip torque. It also adds a small restoring term on the thigh angle.
- **Hidden unit 1 (leg):** a positive bias plus a PD term pushes the knee toward straight, to resist gravity collapsing the leg.
- **Hidden unit 2 (foot):** PD on the foot angle to keep it near neutral.
- **Other 13 hidden units:** zero weights, so they contribute nothing.

The torque signs come from my reading of the Hopper joint axes, which I could not check.

```json
{
"W1": [
[0,5,-1,0,0,0,0,0.5,0,0,0],
[0,0,0,-5,0,0,0,0,0,-0.1,0],
[0,0,0,0,-3,0,0,0,0,0,-0.1],
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
"b1": [0,0.3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```