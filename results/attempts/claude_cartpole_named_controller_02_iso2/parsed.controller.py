def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 4.0 * th + 0.3 * v + 0.5 * w
    return [max(-3.0, min(3.0, u))]
