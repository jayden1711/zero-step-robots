I treated this as the Hopper standing problem: a stiff joint-space PD controller that holds the body upright and still. That should survive all 1000 steps and earn about 1 per step.

**Observation layout assumed (inferred from the spec, not confirmed):**
- obs[0] is height.
- obs[1] is torso pitch.
- obs[2:5] are the hip, knee and ankle angles.
- obs[5:11] are the x velocity, z velocity, torso pitch rate and joint rates.

**How it works:**
- Each action drives one joint with `a = -Kp·q - Kd·q̇`. I used Kp=4 and Kd=0.3 for the hip and knee, and Kp=2 and Kd=0.3 for the ankle.
- With the foot flat and the hip and knee held rigid, the ankle angle equals the body's tilt. So the ankle PD also balances the inverted pendulum. Its 400 Nm/rad of stiffness is above the roughly 87 Nm/rad gravity toppling stiffness.
- Units 0 to 2 hold these terms, scaled by 0.1 so tanh stays nearly linear. W2 multiplies them back by 10.
- All other units are zero.

**Limits:**
- I couldn't run it, so the score is unverified.
- It does not try to move forward, so it gives up the velocity reward in exchange for safety.

```json
{
  "W1": [
    [0, 0, -0.4, 0, 0, 0, 0, 0, -0.03, 0, 0],
    [0, 0, 0, -0.4, 0, 0, 0, 0, 0, -0.03, 0],
    [0, 0, 0, 0, -0.2, 0, 0, 0, 0, 0, -0.03],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "W2": [
    [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b2": [0, 0, 0]
}
```