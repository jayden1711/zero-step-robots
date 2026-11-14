import numpy as np


def reset():
    pass


def act(obs):
    z, ang, q_thigh, q_leg, q_foot = obs[0:5]
    vx, vz, w, w_thigh, w_leg, w_foot = obs[5:11]

    # Keep hip and knee extended against their limits
    a0 = 0.3 - 3.0 * q_thigh - 0.2 * w_thigh
    a1 = 0.3 - 3.0 * q_leg - 0.2 * w_leg

    # Ankle balances the torso: lean forward -> positive foot torque
    a2 = 4.0 * ang + 0.6 * w + 0.15 * vx - 0.5 * q_foot - 0.05 * w_foot

    return [float(np.clip(a0, -1, 1)),
            float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1))]
