I went with a controller that balances the hopper standing still, and I haven't run it. A standing hopper earns about 1 per step, so roughly **1000 per episode**, minus a negligible control cost. A hand-tuned hopping gait could score more, but it can't be tuned without testing. If it falls early, an episode scores tens instead of about 1000.

**Design notes (signs worked out from the Hopper XML: every joint axis is `0 -1 0`)**
- **Angle signs:** a positive world angle means a link's top tips toward −x, i.e. it leans back. The thigh and knee joint limits are `[-150°, 0]`, so the upright pose sits exactly at those limits.
- **Knee:** a small constant positive torque plus PD keeps the knee pressed against its 0 limit. This locks the leg straight.
- **Hip:** the hip keeps the torso upright in the world frame. A positive thigh torque applies a negative reaction torque to the torso, so the hip torque is `+Kp·torso_angle + Kd·torso_angvel`.
- **Ankle:**
  - The ankle uses an "ankle strategy": it estimates where the centre of mass above the ankle sits horizontally, and how fast it moves, from the link angles and approximate link masses.
  - It pushes that point back over the ankle with a PD law. A positive foot torque rotates the leg forward.
  - The proportional gain (≈300 N·m/rad) is well above the gravitational toppling stiffness (≈77 N·m/rad). The damping is near critical. Both are small enough that the foot shouldn't tip over at the tiny initial perturbations.

```python
import math

# Approximate link masses (capsules, density 1000)
M_LEG = 2.78
M_THIGH = 4.06
M_TORSO = 3.67
M_ABOVE = M_LEG + M_THIGH + M_TORSO

L_LEG = 0.5
L_THIGH = 0.45


def reset():
    pass


def _clip(v):
    return max(-1.0, min(1.0, v))


def act(obs):
    torso_ang = obs[1]
    thigh_q = obs[2]
    leg_q = obs[3]
    torso_w = obs[7]
    thigh_w = obs[8]
    leg_w = obs[9]

    # World angles of links (positive = top leans toward -x)
    th_t = torso_ang
    th_th = th_t + thigh_q
    th_l = th_th + leg_q
    w_t = torso_w
    w_th = w_t + thigh_w
    w_l = w_th + leg_w

    s_t, s_th, s_l = math.sin(th_t), math.sin(th_th), math.sin(th_l)
    c_t, c_th, c_l = math.cos(th_t), math.cos(th_th), math.cos(th_l)

    # Horizontal CoM position (relative to ankle) of everything above the ankle
    x_com = (M_LEG * (-0.25 * s_l)
             + M_THIGH * (-L_LEG * s_l - 0.225 * s_th)
             + M_TORSO * (-L_LEG * s_l - L_THIGH * s_th - 0.2 * s_t)) / M_ABOVE
    xd_com = (M_LEG * (-0.25 * c_l * w_l)
              + M_THIGH * (-L_LEG * c_l * w_l - 0.225 * c_th * w_th)
              + M_TORSO * (-L_LEG * c_l * w_l - L_THIGH * c_th * w_th
                           - 0.2 * c_t * w_t)) / M_ABOVE

    # Ankle: keep CoM above the ankle (positive foot torque rotates leg forward)
    u_foot = -2.0 * x_com - 0.4 * xd_com

    # Hip: keep torso upright in world frame
    u_thigh = 0.5 * torso_ang + 0.06 * torso_w

    # Knee: lock straight against its 0 limit
    u_leg = 0.3 - 3.0 * leg_q - 0.2 * leg_w

    return [_clip(u_thigh), _clip(u_leg), _clip(u_foot)]
```