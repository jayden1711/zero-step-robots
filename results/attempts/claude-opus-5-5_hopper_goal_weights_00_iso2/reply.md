This looks like the Hopper task (one leg, three joints). Writing a controller that hops forward without being able to test it is very unreliable. So I aimed for the reliable baseline instead: stand upright and stay healthy for all 1000 steps, which earns about 1 reward per step. This is untested.

**Assumed observation layout:**
- obs[1]: torso pitch
- obs[3]: knee angle; obs[4]: ankle angle
- obs[5]: forward velocity; obs[7]: pitch rate
- obs[9], obs[10]: knee and ankle velocities

**Controller:** three hidden units do the work, each a PD loop kept near the linear part of tanh (input scaled by 0.5, output by 2).
- **Hip** (action 0): pushes the torso back to upright using its pitch and pitch rate.
- **Knee** (action 1): holds the leg straight.
- **Ankle** (action 2): keeps the body balanced over the foot using ankle angle, ankle velocity and forward velocity.

The other 13 hidden units are unused (all zeros).

```json
{
"W1": [
[0, 0.5, 0, 0, 0, 0, 0, 0.05, 0, 0, 0],
[0, 0, 0, -0.5, 0, 0, 0, 0, 0, -0.05, 0],
[0, 0, 0, 0, -0.5, -0.1, 0, 0, 0, 0, -0.15],
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
[2, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0],
[0, 2, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0],
[0, 0, 2, 0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0, 0, 0]
}
```