This is a hand-designed balance controller, untested since I can't run anything. It uses two hidden units:

- **Torso balance:** hidden unit 1 is a PD term on the torso angle and angular velocity. It drives both the thigh and foot torques, with the sign chosen from the Hopper axis conventions (positive torso angle means leaning backward).
- **Leg damping:** hidden unit 2 applies a restoring torque on the leg joint.

The goal is mainly to stay upright for the full episode, which earns about 1 per step.

```json
{"W1":[[0,5,0,0,0,0,0,0.5,0,0,0],[0,0,0,2,0,0,0,0,0,0.1,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]],
"b1":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2":[[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,-0.8,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
"b2":[0,0,0]}
```