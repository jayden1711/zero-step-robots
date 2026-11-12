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
