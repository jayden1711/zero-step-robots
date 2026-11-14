import numpy as np

# Full-state feedback (pole placement, all closed-loop poles at s = -4)
# state: [cart pos, pole angle, cart vel, pole angular vel]
K = np.array([1.23, 6.52, 1.23, 1.24])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
