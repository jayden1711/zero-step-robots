def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 0.3 * xd + 3.5 * th + 0.5 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
