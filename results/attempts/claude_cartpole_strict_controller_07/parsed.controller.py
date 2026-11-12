def reset():
    pass


def act(obs):
    x, th, xd, thd = obs[0], obs[1], obs[2], obs[3]
    u = 0.1 * x + 2.5 * th + 0.2 * xd + 0.4 * thd
    return [max(-3.0, min(3.0, u))]
