import numpy as np

# State feedback gains: [cart pos, pole angle, cart vel, pole ang vel]
K = np.array([0.3, 6.0, 0.6, 1.2])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
