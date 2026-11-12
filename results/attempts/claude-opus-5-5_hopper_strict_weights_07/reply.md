This environment matches MuJoCo **Hopper**: torso height and angle, three joint angles, then six velocities, with three joint torques as actions. Learning a hop by hand is not realistic, so the controller aims for the reliable baseline. It keeps the hopper standing upright for all 1000 steps, which should score about 1000.

**Design.** Each joint gets a stiff PD controller toward its zero angle, which is the upright pose the episode starts from:

- torque_j = −2·q_j − 0.2·q̇_j, in action units.
- This works out to about 400 N·m/rad and 40 N·m·s/rad, assuming the usual gear of 200 and an effective joint inertia of about 1 (armature).
- The upright structure stands on its flat foot, and its center of mass is over the support. Holding it rigid therefore keeps the height above 0.7 and the torso angle near 0.

**How the network does it.** Six hidden units each pass one input through tanh with a small gain, 0.1. The two units per joint read its angle (indices 2, 3, 4) and its angular velocity (indices 8, 9, 10). At that gain, tanh is nearly linear over the range the inputs will see. The output weights are the gains divided by 0.1, so −20 for angle and −2 for velocity. The other ten hidden units and all biases are zero.

```json
{"W1": [[0,0,0.1,0,0,0,0,0,0,0,0],[0,0,0,0.1,0,0,0,0,0,0,0],[0,0,0,0,0.1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0.1,0,0],[0,0,0,0,0,0,0,0,0,0.1,0],[0,0,0,0,0,0,0,0,0,0,0.1],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [[-20,0,0,-2,0,0,0,0,0,0,0,0,0,0,0,0],[0,-20,0,0,-2,0,0,0,0,0,0,0,0,0,0,0],[0,0,-20,0,0,-2,0,0,0,0,0,0,0,0,0,0]],
"b2": [0,0,0]}
```