This controller tries to stand still and balanced for the full 1000 steps. It doesn't try to hop forward. Hopping could earn more, but a fall ends the episode, so standing still is the safer bet when the gait can't be tested first.

**Expected score:** about 1 per step (roughly 1000 per episode), plus or minus a little drift, minus a small torque cost. I haven't run it, so this is an estimate from the dynamics, not a measured result.

How it works:
- **Pose:** it holds a nearly straight leg, with the thigh and knee each bent 0.05 rad. This keeps them slightly away from their joint limits at 0. At a limit, the joint stops pushing back in one direction, which would block corrections.
- **Hip:** the hip torque keeps the torso upright. By the action–reaction rule, a positive hip torque pushes the torso backward, so a forward lean is answered with positive torque. A weak extra pull keeps the thigh near its target.
- **Knee:** a simple spring-and-damper (PD) loop holds it at its target.
- **Ankle:** a PD loop keeps the foot flat, meaning the foot's world angle (torso + thigh + leg + foot) stays at 0. This acts as a stiff ankle spring (about 400 Nm/rad, while gravity's pull to tip over is about 130 Nm/rad), so the body stays balanced over the foot.
- **Ankle limit:** the ankle torque is capped at 0.3, so the foot doesn't roll onto its heel or toe.

```python
import numpy as np

# Nominal standing pose (joint angles, rad); slightly off the 0 joint limits.
THIGH_DES = -0.05
LEG_DES = -0.05


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    torso, q_t, q_l, q_f = obs[1], obs[2], obs[3], obs[4]
    w_torso, qd_t, qd_l, qd_f = obs[7], obs[8], obs[9], obs[10]

    # Hip: keep torso upright (positive hip torque pitches torso back),
    # with a weak pull toward the nominal thigh angle.
    a_t = 3.0 * torso + 0.4 * w_torso \
        - 0.5 * (q_t - THIGH_DES) - 0.05 * qd_t

    # Knee: PD to nominal.
    a_l = -2.0 * (q_l - LEG_DES) - 0.2 * qd_l

    # Ankle: keep the foot flat (world angle of foot = 0).
    foot_world = torso + q_t + q_l + q_f
    foot_world_vel = w_torso + qd_t + qd_l + qd_f
    a_f = -2.0 * foot_world - 0.2 * foot_world_vel
    a_f = float(np.clip(a_f, -0.3, 0.3))

    a = np.clip([a_t, a_l, a_f], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```