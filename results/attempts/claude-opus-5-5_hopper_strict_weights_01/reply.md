This observation layout matches MuJoCo's **Hopper**: obs[0] is torso height, obs[1] is torso angle, obs[2:5] are the thigh, leg and foot joint angles, obs[5:8] are root velocities, and obs[8:11] are joint velocities. Actions are torques for the thigh, leg and foot.

**Approach:** hold all three joints stiffly at zero. At zero joint angles the centre of mass sits over the long foot, so the hopper stands like a rigid body and stays healthy. That should earn about 1 per step, or roughly 1000 per episode, with almost no action cost. Hopping would score more, but hand-written hopping weights are very likely to fall early.

**How the network does it:** it acts as a joint PD controller, giving roughly `action_i ≈ -3·q_i - 0.2·q̇_i`.
- Hidden units 0–2 compute `tanh(0.1·q_i)` from the joint angles, which stays nearly linear.
- Hidden units 3–5 compute `tanh(0.1·q̇_i)` from the joint velocities.
- The output weights are -30 on each angle unit and -2 on each velocity unit.

With Hopper's joint armature of 1, these gains give a well-damped response (damping ratio about 0.7, natural frequency about 20 rad/s). That should stay stable with an 8 ms control step. I couldn't run or test this, so the stability is reasoned, not confirmed.

```json
{
"W1": [
[0,0,0.1,0,0,0,0,0,0,0,0],
[0,0,0,0.1,0,0,0,0,0,0,0],
[0,0,0,0,0.1,0,0,0,0,0,0],
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
[-30,0,0,-2,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-30,0,0,-2,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-30,0,0,-2,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```