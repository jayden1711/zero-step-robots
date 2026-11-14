import numpy as np

KP = 1.0      # joint stiffness (action units per rad)
KD = 0.05     # joint damping
K_ANK = 3.0   # ankle feedback on torso pitch
K_ANK_D = 0.3
K_HIP = 1.0   # hip feedback on torso pitch
K_HIP_D = 0.1


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch, thigh, leg, foot = o[1], o[2], o[3], o[4]
    pitch_d = o[7]
    thigh_d, leg_d, foot_d = o[8], o[9], o[10]

    a_thigh = -KP * thigh - KD * thigh_d - K_HIP * pitch - K_HIP_D * pitch_d
    a_leg = -KP * leg - KD * leg_d
    a_foot = -KP * foot - KD * foot_d - K_ANK * pitch - K_ANK_D * pitch_d

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(x) for x in a]
