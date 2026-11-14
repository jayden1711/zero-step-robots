This observation and action layout matches MuJoCo's Hopper: obs = [z, torso angle, thigh, leg, foot, vx, vz, torso ang-vel, 3 joint velocities], and the actions are torques on the thigh, leg and foot joints.

I couldn't test anything, so I chose a conservative goal: keep the hopper balanced and healthy for all 1000 steps. That earns about 1000 reward per episode. A hand-designed forward hop, with no way to test it, is likely to fall early and score much lower.

The controller works like this:
- **Knee:** held straight against its joint limit with a stiff PD controller and a small bias torque.
- **Hip:** keeps the torso upright using a PD controller on the torso angle and its rate.
- **Ankle:** balances the whole body as an inverted pendulum. It works out the horizontal centre-of-mass offset from the ankle using the link angles and estimated link masses, then applies PD feedback on that offset. The stiffness is set above m·g so the system is stable.
- **Ankle torque limits:** clipped asymmetrically so the foot doesn't tip over its heel or toe.

```python
import math

_prev_com = None


def reset():
    global _prev_com
    _prev_com = None


def _clip(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _com_x(alpha, q_th, q_leg):
    # absolute segment angles about -y: positive => segment top tilts toward -x
    beta = alpha + q_th          # thigh
    gamma = beta + q_leg         # shank
    m_leg, m_th, m_to = 2.78, 4.06, 3.66
    x_knee = -0.5 * math.sin(gamma)
    x_hip = x_knee - 0.45 * math.sin(beta)
    c_leg = -0.25 * math.sin(gamma)
    c_th = x_knee - 0.225 * math.sin(beta)
    c_to = x_hip - 0.2 * math.sin(alpha)
    return (m_leg * c_leg + m_th * c_th + m_to * c_to) / (m_leg + m_th + m_to)


def act(obs):
    global _prev_com
    alpha = obs[1]
    q_th, q_leg, q_f = obs[2], obs[3], obs[4]
    d_alpha = obs[7]
    d_leg = obs[9]

    # Hip: keep torso upright
    a_hip = 0.5 * (alpha - 0.0) + 0.05 * d_alpha

    # Knee: lock straight against the joint limit
    a_knee = -2.0 * (q_leg - 0.0) - 0.05 * d_leg + 0.05

    # Ankle: balance centre of mass over the foot
    com = _com_x(alpha, q_th, q_leg)
    if _prev_com is None:
        dcom = 0.0
    else:
        dcom = (com - _prev_com) / 0.008
    _prev_com = com
    x_d = 0.02
    a_foot = -1.5 * (com - x_d) - 0.5 * dcom
    a_foot = _clip(a_foot, -0.18, 0.09)

    return [_clip(a_hip, -1.0, 1.0), _clip(a_knee, -1.0, 1.0), a_foot]
```