def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.2 * x + 4.0 * th + 0.4 * xd + 0.8 * thd
    return [max(-3.0, min(3.0, u))]
