import numpy as np

# Joint-space gains (action units; actuator gear is 200 N*m per unit)
HIP_KP, HIP_KD = 1.5, 0.15      # torso-upright loop on the hip
KNEE_KP, KNEE_KD = 2.0, 0.2     # keep knee straight
ANK_KP, ANK_KD = 2.0, 0.25      # keep leg perpendicular to foot
ANK_KV = 0.2                    # push back against forward drift


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q_leg, q_foot = o[3], o[4]
    xvel = o[5]
    torso_w = o[7]
    dq_leg, dq_foot = o[9], o[10]

    # Hip torque acts +tau on thigh, -tau on torso: positive torso tilt -> positive tau.
    a_hip = HIP_KP * torso_ang + HIP_KD * torso_w

    a_knee = -KNEE_KP * q_leg - KNEE_KD * dq_leg

    a_ankle = -ANK_KP * q_foot - ANK_KD * dq_foot - ANK_KV * xvel

    a = np.clip([a_hip, a_knee, a_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
