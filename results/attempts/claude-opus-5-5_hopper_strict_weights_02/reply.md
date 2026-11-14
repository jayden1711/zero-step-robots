This is a balance-only controller: it aims to keep the system upright for all 1000 steps and earn about 1000 per episode. It doesn't try to move forward. I couldn't run or test it, so the signs and gains come from reasoning about the physics only.

**How I read the system.** The observation layout looks like a one-legged hopper:
- `obs[0]` is height.
- `obs[1]` is torso pitch.
- `obs[2..4]` are the three joint angles (hip, knee, ankle).
- `obs[5..7]` are the forward velocity, vertical velocity and torso angular velocity.
- `obs[8..10]` are the three joint velocities.

**The controller.** It is a linear controller built from the hidden layer. Each hidden unit computes `tanh(0.1·x)`, which stays close to `0.1·x` in the normal range, and `W2` scales the result back up.

- **Hip (action 0):** a stiff PD loop that holds the hip angle at 0: `a ≈ -2·q_hip - 0.2·q̇_hip`.
- **Knee (action 1):** the same PD loop on the knee angle: `a ≈ -2·q_knee - 0.2·q̇_knee`.
- **Ankle (action 2):** balances the leg like an inverted pendulum. It uses the shin's angle to the vertical, φ = pitch + hip + knee: `a ≈ 1.0·φ + 0.2·φ̇`.
  - When the foot is flat on the ground, this is the same as holding the ankle angle at 0.
  - The stiffness (about 200 Nm/rad if the action is scaled to torque) is above the gravity torque that tips the body over (about 90 Nm/rad), and the damping is near critical.

The remaining hidden units are switched off.

```json
{
"W1": [
[0,0,0.1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0.1,0,0],
[0,0,0,0.1,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0.1,0],
[0,0.1,0.1,0.1,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0.1,0.1,0.1,0],
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
[-20,-2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-20,-2,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,10,2,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```