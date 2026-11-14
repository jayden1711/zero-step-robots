This controller only tries to keep the hopper standing upright and does not attempt to hop. I couldn't run or test it, so the stability and the expected score below are both untested estimates.

**Why balance instead of hopping:** most of the reward is the +1 per healthy step, so standing safely for all 1000 steps earns about 1000. A hopping gait could earn more, but with no way to tune it, one mistake makes the hopper fall and end the episode early.

**How it balances:**

- **Hip and knee:** these joints are held stiff at 0 rad, which is also the edge of their allowed range, so the joint limit helps hold them there. With both locked, the whole body above the ankle moves as one rigid piece.
- **Ankle:** the rigid body then behaves like an upside-down pendulum pivoting at the ankle. While the foot stays flat, the torso angle is minus the foot joint angle. A positive foot torque therefore tips the body forward, and the controller uses it to drive the torso angle back to 0.
- **Ankle gains:** about 300 Nm/rad of stiffness and roughly critical damping (motor gear is 200, so action 1.5 ≈ 300 Nm). Gravity pulls the body over at roughly 60 Nm/rad, so the stiffness is about five times that. The gains are kept small so that the ankle torque from normal-sized errors stays within what the foot can push without tipping over its edge.
- **Saturation:** if the correction is large, it is clipped to ±0.15 so the foot is not levered off the ground.

```python
import numpy as np


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    ang = o[1]
    thigh, leg, foot = o[2], o[3], o[4]
    angv = o[7]
    thigh_v, leg_v, foot_v = o[8], o[9], o[10]

    # stiff PD holding thigh and leg straight (0 is also their joint limit)
    kp, kd = 1.5, 0.15
    a_thigh = -kp * (thigh - 0.0) - kd * thigh_v
    a_leg = -kp * (leg - 0.0) - kd * leg_v

    # ankle strategy: body (rigid above ankle) is an inverted pendulum on the flat foot.
    # positive foot torque rotates the body toward negative torso angle.
    a_foot = 1.5 * ang + 0.3 * angv
    # keep the ankle torque modest so the foot does not tip off its edges
    a_foot = float(np.clip(a_foot, -0.15, 0.15))

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            a_foot]
```