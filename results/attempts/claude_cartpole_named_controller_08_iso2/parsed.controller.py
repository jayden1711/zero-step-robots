def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.02 * x + 0.6 * th + 0.04 * xd + 0.08 * thd
    return [max(-3.0, min(3.0, u))]
