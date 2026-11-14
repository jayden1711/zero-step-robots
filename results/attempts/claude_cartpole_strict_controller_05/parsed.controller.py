def reset():
    pass


def act(obs):
    x, th, xd, thd = obs[0], obs[1], obs[2], obs[3]
    u = 0.1 * x + 7.0 * th + 0.4 * xd + 1.0 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
