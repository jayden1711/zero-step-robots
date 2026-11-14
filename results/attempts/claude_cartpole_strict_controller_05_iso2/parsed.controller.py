def act(obs):
    x, th, v, w = obs[0], obs[1], obs[2], obs[3]
    u = 0.2 * x + 0.5 * v + 4.0 * th + 0.6 * w
    return [max(-3.0, min(3.0, u))]
