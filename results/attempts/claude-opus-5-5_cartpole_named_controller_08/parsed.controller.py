import numpy as np

# State feedback gains: [cart pos, pole angle, cart vel, pole ang vel]
K = np.array([0.2, 4.7, 0.35, 0.63])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(K, s))
    u = max(-3.0, min(3.0, u))
    return [u]
