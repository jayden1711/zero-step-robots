def reset():
    pass


def act(obs):
    x, th, v, w = obs
    u = 0.1 * x + 5.0 * th + 0.25 * v + 0.7 * w
    return [max(-3.0, min(3.0, u))]
