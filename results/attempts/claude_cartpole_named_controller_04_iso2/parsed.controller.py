def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.05 * x + 3.0 * th + 0.15 * v + 0.5 * w
    return [max(-3.0, min(3.0, u))]
