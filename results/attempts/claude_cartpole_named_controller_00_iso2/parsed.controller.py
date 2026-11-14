def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 3.0 * th + 0.3 * xd + 0.4 * thd
    return [max(-3.0, min(3.0, u))]
