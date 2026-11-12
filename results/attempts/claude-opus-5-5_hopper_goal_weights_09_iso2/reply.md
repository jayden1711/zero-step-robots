This is the Hopper-style system: a one-legged robot with 3 joint torques. I chose a conservative stance-holding controller rather than attempting a hopping gait. Each joint gets a proportional-derivative (PD) servo: a corrective torque proportional to the joint angle, plus damping proportional to the joint velocity. The servos hold the joints at the upright initial pose.

**Observation layout assumed:**
- Joint angles are obs[2:5].
- Joint velocities are obs[8:11].
- A positive action increases its joint's angle.

**Why this should stay healthy:**
- With the foot flat, a stiff ankle servo turns any forward or backward lean of the body into a restoring torque.
- That stiffness (about 800 Nm/rad, assuming 200× actuator gear) is well above the gravitational toppling stiffness (about 150 Nm/rad).
- Damping is moderate, so it stays stable at the 0.008 s control step.

**Expected score:** about 1000 per episode, assuming it survives the full 1000 steps with near-zero forward velocity and a negligible action penalty. I haven't run it, so this is an estimate.

```json
{
"W1": [
[0,0,3.0,0,0,0,0,0,0.25,0,0],
[0,0,0,3.0,0,0,0,0,0,0.25,0],
[0,0,0,0,4.0,0,0,0,0,0,0.4],
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
[-1.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-1.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-1.0,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```