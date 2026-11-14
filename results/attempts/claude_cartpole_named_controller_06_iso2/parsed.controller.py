def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 3.0 * th + 0.3 * v + 0.4 * w
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
