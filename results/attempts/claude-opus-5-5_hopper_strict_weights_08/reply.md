This is a PD (proportional-derivative) balance controller. It is designed to keep the hopper upright for all 1000 steps, which earns about +1 per step. It does not try to hop forward, because doing that reliably by hand is very risky.

The design assumes the standard hopper layout. The observation `obs` holds:
- `[z, torso angle, thigh, leg, foot joint angles]`
- then `[x velocity, z velocity, torso angular velocity, thigh, leg, foot joint velocities]`

The three actions are the thigh, leg and foot torques.

- **Joint stiffness:** each action holds its joint at zero, giving a stiff, upright body standing on its flat foot:
  - a position gain of −5 per radian, using hidden units with input scale 2 and output weight −2.5;
  - plus a damping gain of −0.2 per rad/s, using units with input scale 0.5 and output weight −0.4.
- **Torso correction on the foot:** the foot torque also responds to torso pitch (−2 per radian) and torso angular rate (−0.2 per rad/s). This counters any lean while the centre of mass stays over the foot.
- **Staying linear and bounded:** the hidden-layer input scales are small, so tanh acts almost linearly for normal angles. For large velocities it saturates, which caps the damping torque.
- **Unused weights:** the remaining 8 hidden units and all biases are zero.

```json
{"W1": [[0,0,2,0,0,0,0,0,0,0,0],[0,0,0,2,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0.5,0,0],[0,0,0,0,0,0,0,0,0,0.5,0],[0,0,0,0,0,0,0,0,0,0,0.5],[0,2,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0.5,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], "b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], "W2": [[-2.5,0,0,-0.4,0,0,0,0,0,0,0,0,0,0,0,0],[0,-2.5,0,0,-0.4,0,0,0,0,0,0,0,0,0,0,0],[0,0,-2.5,0,0,-0.4,-1.0,-0.4,0,0,0,0,0,0,0,0]], "b2": [0,0,0]}
```