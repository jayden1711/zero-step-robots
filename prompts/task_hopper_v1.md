## The robot and environment

Environment: Gymnasium `Hopper-v5` (MuJoCo), a planar one-legged robot (torso, thigh, leg, foot) that moves in
the x-z plane. Forward is +x.

- Observation (11 numbers, raw, not normalised):
  1. height (z) of the torso
  2. torso angle (radians)
  3. thigh joint angle
  4. leg joint angle
  5. foot joint angle
  6. torso x-velocity
  7. torso z-velocity
  8. torso angular velocity
  9. thigh joint angular velocity
  10. leg joint angular velocity
  11. foot joint angular velocity

  Velocities (6 to 11) are clipped to [-10, 10].
- Action (3 numbers): the torques at the thigh, leg and foot joints, in that order. Values outside [-1, 1] are
  clipped to that range.
- One step is 0.008 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.005).

Reward and episode rules:

- Reward per step = 1 (while the hopper is healthy) + (torso x-velocity, measured over the step) - 0.001 * (sum of
  the squared action values, after clipping).
- The hopper is healthy while all of these hold: torso height z > 0.7; |torso angle| < 0.2 radians; and every
  joint angle and velocity is strictly inside (-100, 100).
- The episode terminates as soon as the hopper is not healthy. Otherwise it is cut off after 1000 steps.
