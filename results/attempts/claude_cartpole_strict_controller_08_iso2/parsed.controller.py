def reset():
    pass

def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 0.3 * xd + 4.0 * th + 0.6 * thd
    return [max(-3.0, min(3.0, u))]
