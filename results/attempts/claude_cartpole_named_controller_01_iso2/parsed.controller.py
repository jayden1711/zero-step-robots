def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 6.0 * th + 0.3 * v + 0.6 * w
    return [max(-3.0, min(3.0, u))]
