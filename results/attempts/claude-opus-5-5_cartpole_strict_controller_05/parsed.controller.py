import numpy as np

# State feedback: [cart position, pole angle, cart velocity, pole angular velocity]
K = np.array([0.4, 4.5, 0.6, 0.6])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(o)):
        return [0.0]
    u = float(np.dot(K, o))
    u = max(-3.0, min(3.0, u))
    return [u]
