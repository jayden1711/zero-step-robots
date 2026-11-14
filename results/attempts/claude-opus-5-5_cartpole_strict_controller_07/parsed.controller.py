import numpy as np

# State-feedback gains: action = K . [x, theta, x_dot, theta_dot]
# Inner loop (pole angle PD) with a slow outer loop on cart position/velocity
# folded in via a shifted angle reference: theta_ref = -(KP_X*x + KD_X*x_dot).
K_THETA = 5.0
K_OMEGA = 1.0
KP_X = 0.06
KD_X = 0.12


def reset():
    pass


def act(obs):
    x = float(obs[0])
    theta = float(obs[1])
    x_dot = float(obs[2])
    theta_dot = float(obs[3])

    if not all(np.isfinite([x, theta, x_dot, theta_dot])):
        return [0.0]

    theta_ref = -(KP_X * x + KD_X * x_dot)
    theta_ref = float(np.clip(theta_ref, -0.08, 0.08))

    a = K_THETA * (theta - theta_ref) + K_OMEGA * theta_dot
    a = float(np.clip(a, -3.0, 3.0))
    return [a]
