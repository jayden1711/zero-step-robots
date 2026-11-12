import numpy as np

# Joint posture gains (hip, knee): hold straight against the joint limit at 0.
KP_JOINT = 2.0
KD_JOINT = 0.1
BIAS_JOINT = 0.15

# Ankle balance gains (inverted pendulum about the ankle).
K_ANKLE = 1.5
D_ANKLE = 0.3
LEAN_TARGET = 0.02   # slight forward lean to centre COM over foot support
ANKLE_LIMIT = 0.35


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    rooty = obs[1]
    q_t, q_l, q_f = obs[2], obs[3], obs[4]
    rooty_d = obs[7]
    qd_t, qd_l, qd_f = obs[8], obs[9], obs[10]

    # Hip and knee: PD toward 0 plus a small push into the straight-leg limit.
    a_thigh = KP_JOINT * (0.0 - q_t) - KD_JOINT * qd_t + BIAS_JOINT
    a_leg = KP_JOINT * (0.0 - q_l) - KD_JOINT * qd_l + BIAS_JOINT

    # Absolute forward lean of the shank (positive = top toward +x).
    psi = rooty - q_t - q_l
    psi_d = rooty_d - qd_t - qd_l

    # Positive foot torque tips the shank forward, so feed back negatively.
    a_foot = -(K_ANKLE * (psi - LEAN_TARGET) + D_ANKLE * psi_d)
    a_foot = float(np.clip(a_foot, -ANKLE_LIMIT, ANKLE_LIMIT))

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            a_foot]
