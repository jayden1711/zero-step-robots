def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 4.0 * th + 0.25 * v + 0.5 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
