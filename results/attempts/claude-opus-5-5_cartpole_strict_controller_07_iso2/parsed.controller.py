import numpy as np

# Gains: [cart_pos, pole_angle, cart_vel, pole_ang_vel]
K = np.array([0.15, 5.0, 0.3, 0.8])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    a = float(np.dot(K, o))
    a = max(-3.0, min(3.0, a))
    return [a]
