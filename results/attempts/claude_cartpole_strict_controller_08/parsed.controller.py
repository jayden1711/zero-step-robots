def reset():
    pass


def act(obs):
    x, th, xd, thd = obs[0], obs[1], obs[2], obs[3]
    u = 0.05 * x + 3.0 * th + 0.15 * xd + 0.4 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [u]
