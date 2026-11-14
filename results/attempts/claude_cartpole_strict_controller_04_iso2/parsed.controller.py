def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.2 * x + 8.0 * th + 0.5 * xd + 1.5 * thd
    return [max(-3.0, min(3.0, u))]
