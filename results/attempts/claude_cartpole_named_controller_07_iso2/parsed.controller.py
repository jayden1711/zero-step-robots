def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 4.0 * th + 0.6 * w + 0.1 * x + 0.2 * v
    return [max(-3.0, min(3.0, u))]
