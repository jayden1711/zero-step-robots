Approach: the bottom row of the network is a PD controller that holds the hopper upright and still. I could not test anything, so I chose a controller that should reliably stay healthy for all 1000 steps. That should score about 1000, minus a negligible control cost. A hand-designed forward-hopping gait written blind would very likely fall early and score much less.

**How the network implements the controller:**
- **Hidden units 0–2** take the thigh, leg and foot joint angles with input weight 1. This keeps tanh close to linear for small angles, and it still pushes back in the right direction when it saturates.
- **Hidden units 3–5** take the three joint angular velocities scaled by 0.1. This keeps them in tanh's linear range across the clipped ±10 velocity range.
- **The output layer** gives each joint the torque −2·angle − 1·tanh(0.1·velocity). That is about 400 N·m/rad of stiffness and 20 N·m·s/rad of damping after the gear ratio of 200. Hopper's joint armature keeps these gains stable at dt = 0.008.
- **Why it should stand:** holding every joint at 0 makes the hopper a rigid body standing on its flat foot. Its centre of mass sits over the foot, so the torso stays upright, well inside the 0.2 rad tilt limit, and the torso height stays near 1.25.
- **Unused units:** units 6–15 and all biases are zero.

```json
{
"W1": [
[0,0,1,0,0,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0.1,0,0],
[0,0,0,0,0,0,0,0,0,0.1,0],
[0,0,0,0,0,0,0,0,0,0,0.1],
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
[-2,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-2,0,0,-1,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-2,0,0,-1,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```