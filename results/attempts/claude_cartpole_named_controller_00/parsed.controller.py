def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 3.0 * th + 0.45 * thd + 0.1 * x + 0.25 * xd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
