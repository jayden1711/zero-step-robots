def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 4.0 * th + 0.3 * xd + 0.6 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
