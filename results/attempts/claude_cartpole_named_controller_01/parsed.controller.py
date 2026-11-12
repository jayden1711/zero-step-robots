def act(obs):
    x, th, xd, thd = obs
    u = 0.1 * x + 3.0 * th + 0.2 * xd + 0.4 * thd
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
