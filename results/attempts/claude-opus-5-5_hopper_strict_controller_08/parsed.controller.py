import numpy as np

# Joint PD gains (action units per rad, per rad/s)
KP_HIP, KD_HIP = 3.0, 0.3
KP_KNEE, KD_KNEE = 3.0, 0.3
KP_ANKLE, KD_ANKLE = 2.0, 0.4
# Extra torso-pitch correction through the hip
KP_TORSO, KD_TORSO = 1.0, 0.1


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    q_hip, q_knee, q_ankle = o[2], o[3], o[4]
    pitch_d = o[7]
    qd_hip, qd_knee, qd_ankle = o[8], o[9], o[10]

    a_hip = -KP_HIP * q_hip - KD_HIP * qd_hip
    # hip torque reaction leans torso forward for positive action -> push back on forward pitch
    a_hip += -KP_TORSO * pitch - KD_TORSO * pitch_d

    a_knee = -KP_KNEE * q_knee - KD_KNEE * qd_knee

    a_ankle = -KP_ANKLE * q_ankle - KD_ANKLE * qd_ankle

    a = np.clip([a_hip, a_knee, a_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
