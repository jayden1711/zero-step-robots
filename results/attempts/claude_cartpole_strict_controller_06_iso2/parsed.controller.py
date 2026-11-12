def reset():
    pass


def act(obs):
    x, th, xd, thd = obs[0], obs[1], obs[2], obs[3]
    u = 0.3 * x + 8.0 * th + 0.5 * xd + 1.0 * thd
    return [max(-3.0, min(3.0, u))]
