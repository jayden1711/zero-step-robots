This controller holds the hopper upright and still rather than hopping, aiming for roughly 1000 points. I worked it out by hand and couldn't run anything, so that figure is not tested.

**Why standing:** with all joint angles at 0, the body's centre of mass sits over the flat foot, which reaches from 0.13 behind the ankle to 0.26 in front. If the joints are held stiff, the hopper should stay healthy for the full 1000 steps. Each step earns 1, so an episode scores about 1000, minus a negligible action cost. A hand-written hopping gait could score more, but if it falls early the score drops sharply, so I chose the safer option.

**How it works:** each joint gets its own saturating spring-damper that pulls it back to 0. Hidden units 0, 1 and 2 are:

- thigh: `tanh(2.0·q + 0.10·q̇)`
- leg: `tanh(2.0·q + 0.15·q̇)`
- foot: `tanh(2.0·q + 0.10·q̇)`

Each is fed back with weight −1, so `action_j = −tanh(Kp·q_j + Kd·q̇_j)`. The tanh keeps every action inside [−1, 1] automatically.

**Why those gains:**
- Each motor multiplies the action by 200, so a stiffness of 2 is about 400 Nm per radian.
- That is about three times the gravity torque that tips the robot over (about 130 Nm per radian).
- The damping should be enough to stop oscillation at the 0.008 s step.
- Holding the ankle at 0 keeps the leg vertical, holding the knee and hip at 0 keeps the rest of the body in line, and so the torso angle stays near 0.

The other 13 hidden units are unused (all their weights are 0).

```json
{
  "W1": [
    [0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0],
    [0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.15, 0.0],
    [0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ],
  "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "W2": [
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ],
  "b2": [0.0, 0.0, 0.0]
}
```