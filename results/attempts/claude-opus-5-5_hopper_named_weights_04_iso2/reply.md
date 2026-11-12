This controller tries to make the hopper stand still and balanced for the full 1000 steps, which earns about 1 point per step (roughly 1000 per episode). It does not try to hop forward. Designing a hopping gait by hand with no way to test it risks early falls, so standing was the safer choice. I have not run it, so the score is unverified.

**How it works:** 8 of the 16 hidden units are used, each reading one observation. The input weights are small, so each tanh stays in its near-linear range and passes its value through almost unchanged. The output layer then forms a PD (spring-and-damper) controller:

- **Joint holding:** each joint (thigh, leg, foot) is held at angle 0 with a torque of about −2·angle − 0.05·angular velocity, in action units. This keeps the body nearly rigid. The centre of mass then sits above the foot, which reaches from x = −0.13 to 0.26, so the body stays up on its own.
- **Torso balance:** feedback on the torso angle and its angular velocity goes to the hip (−0.5·θ) and the ankle (−1·θ). These torques push the body back toward upright before it reaches the 0.2 rad tilt limit.
- **Stability of the gains:** the gains are kept moderate (about 400 Nm/rad stiffness, about 10 Nms/rad damping). This keeps the controller stable with the 0.008 s control step.
- **Action cost:** the actions stay small, so the action-cost penalty is negligible.

```json
{
"W1": [
[0,1,0,0,0,0,0,0,0,0,0],
[0,0,1,0,0,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0.2,0,0,0],
[0,0,0,0,0,0,0,0,0.2,0,0],
[0,0,0,0,0,0,0,0,0,0.2,0],
[0,0,0,0,0,0,0,0,0,0,0.2],
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
[-0.5,-2.0,0,0,-0.25,-0.25,0,0,0,0,0,0,0,0,0,0],
[0,0,-2.0,0,0,0,-0.25,0,0,0,0,0,0,0,0,0],
[-1.0,0,0,-2.0,-0.25,0,0,-0.25,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```