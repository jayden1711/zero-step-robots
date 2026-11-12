def reset():
    pass


def act(obs):
    x, theta, v, w = obs
    u = 0.1 * x + 0.3 * v + 6.0 * theta + 0.8 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
