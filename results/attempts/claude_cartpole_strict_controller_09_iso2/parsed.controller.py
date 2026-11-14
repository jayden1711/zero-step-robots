def reset():
    pass

def act(obs):
    x, th, xd, thd = obs
    u = 0.3 * x + 6.0 * th + 0.5 * xd + 0.8 * thd
    return [max(-3.0, min(3.0, u))]
