def reset():
    pass


def act(obs):
    x, th, v, w = obs[0], obs[1], obs[2], obs[3]
    a = 0.1 * x + 3.0 * th + 0.3 * v + 0.45 * w
    if a > 3.0:
        a = 3.0
    elif a < -3.0:
        a = -3.0
    return [a]
