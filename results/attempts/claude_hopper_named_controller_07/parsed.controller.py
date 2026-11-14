import numpy as np


def reset():
    pass


def act(obs):
    theta = obs[1]
    q1, q2, q3 = obs[2], obs[3], obs[4]
    w0 = obs[7]
    w1, w2, w3 = obs[8], obs[9], obs[10]

    # Ankle: PD on torso lean (positive lean = backward, positive torque corrects it)
    a3 = 3.0 * (theta + 0.3 * (q1 + q2 + q3)) + 0.5 * w0 - 0.02 * w3

    # Hold hip and knee extended against their joint limits at 0
    a1 = 0.25 - 0.03 * w1
    a2 = 0.35 - 0.03 * w2

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
