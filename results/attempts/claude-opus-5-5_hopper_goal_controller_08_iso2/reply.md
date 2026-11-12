This controller aims for a reliable score of about **1000** by balancing in place for the full 1000 steps. It does not try to hop forward. I couldn't run or test it, so the gains and signs come from working through the physics by hand, not from simulation.

**Why not hop?** The observations, actions and health rules match the MuJoCo Hopper. A forward-hopping gait could score about 2000–3000. But a gait designed without any testing would very likely fall early, and an early fall scores well under 1000. Staying upright for all 1000 steps earns about 1 per step, so I chose that.

**How it balances:**
- **Hip and knee (actions 0 and 1):** Both joints can only bend one way from straight. Each is held straight by a PD controller with a small positive bias that presses it against its joint limit. That makes the body behave like one rigid stick above the ankle.
- **Ankle (action 2):** This joint balances the stick like an inverted pendulum.
  - The lean angle of the stick is `obs[1] - obs[2] - obs[3]` (torso angle minus hip and knee angles).
  - A positive ankle torque tips the body forward when the foot is on the ground.
  - The target lean is slightly forward, so the centre of mass sits over the middle of the foot, which extends further forward of the ankle than behind it.
- **Ankle limits:** The ankle command is limited to ±0.2. A larger torque could lift the toe or heel off the ground.
- **Gains:** They were sized from estimated body masses and lengths: gravity pulls with about 78 Nm per radian of lean, the actuator gives 200 Nm per unit of action, and the inertia about the ankle is about 7.5 kg·m². The ankle loop is set close to critical damping.

```python
import numpy as np

# Target lean (rad) of the rigid leg+torso stick about the ankle; slightly
# forward so the centre of mass sits over the middle of the foot.
PHI_TARGET = 0.04

KP_ANKLE = 1.5
KD_ANKLE = 0.35
ANKLE_LIM = 0.2

KP_JOINT = 3.0
KD_JOINT = 0.15
JOINT_BIAS = 0.15   # press hip/knee into their straight (0) limit


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    theta, q_thigh, q_leg, q_foot = obs[1], obs[2], obs[3], obs[4]
    dtheta, dq_thigh, dq_leg = obs[7], obs[8], obs[9]

    # Hip and knee: hold straight, biased into the joint limit.
    a_hip = KP_JOINT * (0.0 - q_thigh) - KD_JOINT * dq_thigh + JOINT_BIAS
    a_knee = KP_JOINT * (0.0 - q_leg) - KD_JOINT * dq_leg + JOINT_BIAS

    # Ankle: balance the stick as an inverted pendulum.
    phi = theta - q_thigh - q_leg
    dphi = dtheta - dq_thigh - dq_leg
    a_foot = -KP_ANKLE * (phi - PHI_TARGET) - KD_ANKLE * dphi
    a_foot = float(np.clip(a_foot, -ANKLE_LIM, ANKLE_LIM))

    a = np.clip([a_hip, a_knee, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```